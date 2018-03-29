window.addEventListener("load", function () {
    // Sign in
    var signInBtn = document.querySelector('.login-btn');
    if (signInBtn) {
        signInBtn.addEventListener('submit', function(event) {
            event.preventDefault();
            main.auth.signIn(event, this);
        });
    }
    // Register
    var signUpBtn = document.querySelector('.sign-up');
    if (signUpBtn) {
        signUpBtn.addEventListener('submit', function(event) {
            event.preventDefault();
            main.auth.signUp(event, this);
        });
    }
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
            var url = '/account/login_async/'; // default form action url
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
                    document.location.href = '/';
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
            $('#login-modal').modal('hide');
        }
    },
};

main.utils = {
    arrayToHtmlList: (arr, listID) =>
      arr.map(item => (document.querySelector('#' + listID).innerHTML += `<li>${item}</li>`))
};
