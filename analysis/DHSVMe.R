#
# DHSVMe.R -- DHSVM emulator
# Predict DHSVM output.
# 2018-06-26, WAH.
#==============================================================================#
time.0 <- Sys.time()
message("---------------------------------------------------------------\n",
        "DHSVM emulator v0.1 beta.  (c) 2018 SSPA.  All rights reserved.\n", 
        "---------------------------------------------------------------")
#
# Third-party libraries.
#
require(data.table, quietly=TRUE)
#..............................................................................#
#
# RUNTIME PARAMETERS
#
# These are designed to be modifiable through command-line arguments.
# Example:
#
#   rscript DHSVMe.R -c ../Data/Models/ -i ../inputs/example_input.csv > output.csv
#
# Result:
#
# ---------------------------------------------------------------
# DHSVM emulator v0.1 beta.  (c) 2018 SSPA.  All rights reserved.
# ---------------------------------------------------------------
# INFO:  'path.data' set to '../Data/Models/'
# INFO:  'fn.in' set to '../inputs/example_input.csv'
# Predicting during water year 1997 for 15 locations.
# 43,785 predicted flows created for 15 locations.
# 0.94 secs; 53.94 MB RAM allocated.
#
arguments <- list(
  c = list(path.data = ""),                # Where to read the coefficient files
  t = list(template = "Coeff_*.RData"),    # Coefficient file template
  i = list(fn.in = "Pourpoints.csv"),      # Input file
  o = list(fn.out = stdout()),             # Output connection
  f = list(fmt.date = "%m.%d.%Y-%H:%M:%S") # Input date-time format
)
parse.args <- function(arguments, args=commandArgs(trailingOnly=TRUE)) {
  emit <- function(...) cat("INFO: ", ..., "\n", file=stderr())
  q <- function(s, ...) paste0("'", s, "'", ...)
  
  rx <- paste0("^[-][", paste0(names(arguments), collapse=""), "]")
  current.arg <- ""
  nerrs <- 0
  for (arg in args) {
    # emit("Argument ", arg)
    if (current.arg == "") {
      if (grepl(rx, arg)) {
        current.arg <- substr(arg, 2, 2)
        # emit("Processing", current.arg)
        if (nchar(arg) > 2) arg <- substr(arg, 3, nchar(arg)) else arg <- ""
      } else {
        emit("Unexpected command-line argument", arg)
        current.arg <- arg <- ""
        nerrs <- nerrs + 1
      }
    }
    if (current.arg != "" && arg != "") {
      temp <- arguments[[current.arg]]
      temp[[1]] <- arg
      arguments[[current.arg]] <- temp
      emit(q(names(arguments[current.arg][[1]])[1]), "set to", q(arg))
      current.arg <- ""
    }
  }
  if (nerrs > 0) {
    emit("Recognized arguments are", paste0("-", names(arguments)))
    stop(call.=FALSE)
  }
  arguments
}
arguments <- parse.args(arguments)
for (a in arguments) {
  assign(names(a)[1], a[[1]])
}
#
# More obscure configuration parameters.
#
wateryear.min <- 1989                   # First available water year
wateryear.max <- 2015                   # Last available water year
#------------------------------------------------------------------------------#
#
# HELPER FUNCTIONS
#
# General-purpose, automatic error handling.
#
assure <- function(exp, message) {
  x <- suppressWarnings(tryCatch(exp, error=function(e) e))
  if (inherits(x, "error")) {
    if (!missing(message)) message(message)
    message(x$message)
    stop(call.=FALSE)
  }
  x
}
#
# Date-time conversion.
#
to.Date <- function(s, f=fmt.date) as.POSIXct(strptime(s, format=f))
waterYear <- function(d, delta=as.difftime(31+30+31+1/24, units="days")) {
  format(d + delta, "%Y") # Character type
}
#------------------------------------------------------------------------------#
#
# READ AND CHECK THE INPUT FILE
#
X <- assure(as.data.table(read.csv(file=fn.in, stringsAsFactors=FALSE)),
            paste0("Unable to read input from file '", fn.in, 
                   "'.  Reason given is:"))
#
# Check that field names and types are as expected.
#
vars.key <- c(
  ppt_ID="ppt_ID",          # Passed to output
  start_time="start_time",  # Selects time slices
  end_time="end_time"       # Selects time slices
) 
vars.stations <- c(
  # mazama="MAZAMA_NOAA", # Needed only for checking sum-to-unity criterion
  winthrop="Winthrop",
  plain="Plain",
  poperidge="PopeRidge",
  trinity="Trinity"
)
vars.static <- c(
  SDsphrical="SD.Spherical",
  area="acres",
  avg_slp="mean_slope",
  slp_gt60="slp_gt60",
  mean_elev="mean_elevation",
  elev_dif="elev_dif",
  mean_shade="mean_shade",
  veg_prop="veg_prop",
  bulk_dens="bulk_dens",
  cap_drv="cap_drv",
  exp_decrs="exp_decrs",
  field_cap="field_cap",
  lat_con="lat_con",
  mannings="mannings",
  pore_sz="pore_sz",
  porosity="porosity",
  vert_con="vert_con",
  wilt_pt="wilt_pt",
  bbl_prsr="bbl_prsr",
  max_inf="max_inf"
)
vars.scenario <- c(
  thc_11="thc_11",
  thc_12="thc_12",
  thc_13="thc_13",
  thc_14="thc_14",
  thc_15="thc_15",
  thc_21="thc_21",
  thc_22="thc_22",
  thc_23="thc_23",
  thc_24="thc_24",
  thc_25="thc_25"
)
vars <- c(vars.key, vars.stations, vars.static, vars.scenario)
a <- vars[names(X)]
a <- a[!is.na(a)]
if(length(a <- setdiff(vars, a)) > 0) {
  message("Some variables are missing from input: \n",
          paste(a, collapse=", "))
  stop(call.=FALSE)
}
#
# Check for unique identifiers.
#
if (any(duplicated(X[, .(ppt_ID)]))) {
  message("Duplicate record identifiers found in input: please make sure they are unique.")
  stop(call.=FALSE)
}
#
# Verify that all variables indeed look numeric (except for the keys).
#
varnames <- setdiff(names(vars), names(vars.key))
type.number <- sapply(varnames, 
                      function(f) inherits(X[[f]], c("integer", "numeric")))
if(sum(!type.number) > 0) {
  message("These variables are not all numeric:\n",
          paste(varnames[!type.number], collapse=", "))
  stop(call.=FALSE)
}
#
# Convert the time specifiers into date-time fields.
#
i.start <- is.na(to.Date(X$start_time))
i.end <- is.na(to.Date(X$end_time))
if (any(i.start) || any(i.end)) {
  message("Not all start and end date-times could be parsed using format '", 
          fmt.date, "\nThe unknown values are:\n",
          paste(c(X$start_time[i.start], X$end_time[i.end]), collapse=", "))
  stop(call.=FALSE)
}
invisible({
  X[, c("start_time", "end_time") := list(to.Date(start_time), to.Date(end_time))]
})
#
# Translate to the names used when fitting the models.
#
X <- X[, names(vars), with=FALSE]
names(X) <- vars
#------------------------------------------------------------------------------#
#
# Establish the range of water years to process.
#
delta <- as.difftime(1, units="secs")
X <- X[order(start_time)]
w <- as.numeric(waterYear(c(min(X$start_time), max(X$end_time) - delta)))
wateryears <- pmin(wateryear.max, pmax(wateryear.min, w))
if (length(setdiff(w, wateryears)) > 0) {
  warning("Restricting dates to ", wateryears[1], " to ", wateryears[2], ".\n",
          "If this seems wrong, set command-line arguments for ",
          "wateryear.min and wateryear.max.")
}
wateryears <- seq(wateryears[1], wateryears[2], by=1)
#..............................................................................#
#
# The guts of the thing.
#
process <- function(X, wateryear) {
  #
  # Restrict to pourpoints that need the file for this water year.
  #
  X0 <- X[waterYear(end_time) >= wateryear & wateryear >= waterYear(start_time)]
  if (nrow(X0)==0) return(NULL)
  message("Predicting during water year ", wateryear,
          " for ", nrow(X0), " locations.")
  #
  # Read the coefficient file.
  #
  fn.coeff <- sub("[*]", wateryear, template)
  fn <- list.files(path.data, fn.coeff, full.names=TRUE)
  if (length(fn) == 0) {
    message("Unable to find coefficient file ", fn.coeff, " for water year ", wateryear, 
            " in path ", path.data)
    return(NULL)
  }
  wy <- wateryear
  objects <- load(fn) # `coefficients`, `xform`, `xform.inverse`, `model.formula`, `wateryear`
  if (length(setdiff(c("coefficients", "xform.inverse", "wateryear"), objects)) > 0) {
    message("Contents of file ", fn, " are incomplete.")
    return(NULL)
  }
  if (wy != wateryear) {
    message("Wrong water year found in file ", fn)
    stop(call.=FALSE)
  }
  #
  # Create a model matrix for X0.
  # The commented-out code creates it from the specifications here.  The
  # actual code creates it from the same formula `model.formula` used to fit
  # the models in the first place.
  #
  for (v in vars.scenario) {
    invisible(X0[, c(v) := X0[[v]] / acres]) # Use per-acre values
  }
  # paren <- function(s) paste0("(", s, ")")   # Parenthesize a string
  # iv.interaction <-  paste(c(vars.scenario, vars.stations), collapse="+")
  # iv.static <- paste(vars.static, collapse="+")
  # f <- as.formula(paste("~", paren(iv.interaction), "*", paren(iv.static)))
  f <- update(model.formula, ~ . + 1) # Include the intercept
  x <- model.matrix(f, X0)
  #
  # Check for consistency between the variables in the model and the variables
  # present in input.
  #
  if (length(v <- setdiff(colnames(x), rownames(coefficients))) > 0) {
    message("Variables were found that are not included in the models for water year ", 
            wateryear, ":\n",
            paste(v, collapse=", "))
    return(NULL)
  }
  if (length(v <- setdiff(rownames(coefficients), colnames(x))) > 0) {
    warning("Variables found in the models for water year ", 
            wateryear, "will not be used:\n",
            paste(v, collapse=", "))
  }
  #
  # Compute. The result is a (number pour points) * (num time slices) matrix.
  # Time slices are given by column names of coefficients.
  #
  v <- intersect(rownames(coefficients), colnames(x)) # Assures a correctly aligned product
  y.hat <- x[, v] %*% coefficients[v, ]               # Log net flow
  #
  # Format as tuples(ID, Time, Value).
  #
  dates <- as.POSIXct(as.numeric(colnames(coefficients)), 
                      origin=as.Date("1970-01-01")) 
  Y <- data.table(ppt_ID=rep(X0$ppt_ID, each=ncol(coefficients)),
                  Time=rep(dates, nrow(X0)),
                  Response=c(t(y.hat)))
  #
  # Select by start and end times.
  #
  # Do this by joining the information from X0, selecting, and then
  # discarding the date ranges.
  #
  Y <- X0[, .(start_time, end_time, acres), keyby=ppt_ID][Y, on="ppt_ID"]
  #
  # Complete the calculations: inverse-transform the
  # raw `Response` to obtain the flows, multiply the flows
  # by the areas, and sort by time within pourpoint.
  #
  Y[start_time <= Time & Time < end_time, 
    .(Value=xform.inverse(Response) * acres), keyby=.(ppt_ID, Time)]
}
#..............................................................................#
#
# Process by ascending water year.
#
Y.list <- lapply(wateryears, function(w) process(X, w))
Y.list <- Y.list[sapply(Y.list, function(x) !is.null(x))]
if (length(Y.list) > 0) {
  Y <- rbindlist(Y.list)
  invisible(Y[, Time := format(Time, fmt.date)])
  write.csv(Y, file=fn.out, row.names=FALSE)
  message(format(nrow(Y), big.mark=","),
          " predicted flows created for ", nrow(X), " locations.")
  time.1 <- Sys.time()
} else {
  message("Nothing was predicted!")
}
#
# Sign off.
#
message(format(round(as.difftime(time.1 - time.0, units="secs"), 2)), "; ",
        memory.size(max=TRUE), " MB RAM allocated.")

