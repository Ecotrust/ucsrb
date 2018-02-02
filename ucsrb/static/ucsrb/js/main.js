window.addEventListener("load", function () {
  // Sign in
  document.getElementById('sign-in').addEventListener('submit', function(event) {
    event.preventDefault();
    main.auth.signIn(event, this);
  });
  // Register
  document.getElementById('sign-up').addEventListener('submit', function(event) {
    event.preventDefault();
    main.auth.signUp(event, this);
  });
  // Sign out
  document.getElementById('menu').addEventListener('click', function(event) {
    if (event.target.nodeName == 'BUTTON') {
      event.preventDefault();
      if (event.target.dataset.action == 'sign-out') {
        main.auth.signOut();
      } else if (event.target.dataset.action == 'sign-in-modal') {
        $('#login-modal').modal('show');
      }
    }
  });
});

var main = {
  auth: {
    signIn: function(event, form) {
      var formData = $(form).serialize();
      var url = 'sign_in/'; // default form action url
        // check if a different action should be used for url
        if (event.target.action.length > 0) {
          url = event.target.action;
        }
      $.ajax({
        url: url,
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: function (data) {
          console.log(data);
          main.auth.success();
        }
      })
    },
    signOut: function(event) {
      $.ajax({
        url: 'sign_out/',
        success: function (data) {
          console.log(data);
        }
      })
    },
    signUp: function(event, form) {
      var formData = $(form).serialize();
      var url = 'sign_up/'; // default form action url
        // check if a different action should be used for url
        if (event.target.action.length > 0) {
          url = event.target.action;
        }
      $.ajax({
        url: url,
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: function (data) {
          main.auth.success();
          console.log(data);
        }
      })
    },
    success: function() {
      var saveState = app.request.saveState();
      if (saveState == 'success') {
        document.location.reload();
      } else {
        document.location.reload();
      }
      $('#login-modal').modal('hide');
    }
  },
}
