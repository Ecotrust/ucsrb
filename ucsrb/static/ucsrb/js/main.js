window.addEventListener("load", function () {
  document.getElementById('sign-in').addEventListener('submit', function(event) {
    event.preventDefault();
    main.auth.signIn(event, this);
  });
  document.getElementById('sign-out').addEventListener('click', function(event) {
    event.preventDefault();
    main.auth.signOut();
  })
});

var main = {
  auth: {
    signIn: function(event, form) {
      var formData = $(form).serialize();
      if (event.target.action.length > 0) {
        var url = event.target.action;
      } else {
        var url = 'sign_in/'
      }
      $.ajax({
        url: url,
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: function (data) {
          console.log('yes');
          main.auth.signInSuccess();
        }
      })
      .done(function() {
        console.log('yes');
        main.auth.signInSuccess();
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
    signInSuccess: function() {
      $('#login-modal').modal('hide');
    }
  },
}
