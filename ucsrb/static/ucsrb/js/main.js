window.addEventListener("load", function () {
    // Sign in
    var signInBtn = document.querySelector('.sign-in');
    if (signInBtn) {
        signInBtn.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('clicked');
            main.auth.signIn(event, this);
        });
    }
    // Register
    var signUpBtn = document.querySelector('#register-form');
    if (signUpBtn) {
        signUpBtn.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('clicked');
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
                url: '/account/logout/',
                success: function (data) {
                    document.location.href = '/';
                }
            })
        },
        signUp: function(event, form) {
            var formData = $(form).serialize();
            var url = '/account/register_async/';
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
        success: function() {
            $('#login-modal').modal('hide');
        }
    },
};

main.utils = {
    arrayToHtmlList: (arr, listID) =>
      arr.map(item => (document.querySelector('#' + listID).innerHTML += `<li>${item}</li>`))
};
