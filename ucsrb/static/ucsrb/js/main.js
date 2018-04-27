window.addEventListener("load", function () {
    // Sign in
    var signInBtn = document.querySelector('.sign-in');
    // Register
    var registerBtn = document.querySelector('#register-form');

    $('#login-modal').on('shown.bs.modal', function(event) {
        if (signInBtn) {
            signInBtn.addEventListener('submit', function(event) {
                event.preventDefault();
                console.log('clicked');
                main.auth.signIn(event, this);
            });
        }
        if (registerBtn) {
            registerBtn.addEventListener('submit', function(event) {
                event.preventDefault();
                console.log('clicked');
                main.auth.register(event, this);
            });
        }
    });

    $('#login-modal').on('hidden.bs.modal', function(event) {
        // if (signInBtn) {
        //     signInBtn.removeEventListener('submit');
        // }
        // if (registerBtn) {
        //     registerBtn.removeEventListener('submit');
        // }
    });

    // Sign out
    document.getElementById('menu').addEventListener('click', function(event) {
        if (event.target.nodeName == 'BUTTON') {
            event.preventDefault();
            if (event.target.dataset.action == 'sign-out') {
                main.auth.logOut();
            } else if (event.target.dataset.action == 'sign-in-modal') {
                $('#login-modal').modal('show');
            }
        }
    });

    document.getElementById('sign-in-modal-2').addEventListener('click', function(event) {
        $('#login-modal').modal('show');
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
                    main.auth.success(data);
                }
            })
        },
        logOut: function(event) {
            $.ajax({
                url: '/account/logout/',
                success: function (data) {
                    document.location.href = '/';
                }
            })
        },
        register: function(event, form) {
            var formData = $(form).serialize();
            var url = '/account/register_async/';
            $.ajax({
                url: url,
                type: 'POST',
                data: formData,
                dataType: 'json',
                success: function (data) {
                    console.log(data);
                    if (data.success === true) {
                        main.auth.success();
                    } else {
                        document.querySelector('#registration-error').innerHTML = `${data.error}. Please update then submit`;
                    }
                }
            })
        },
        success: function(data) {
            console.log(data);
            $('#login-modal').modal('hide');
            // // Hide menu nav login and create account button
            var $signInBtn = $('button#sign-in-modal');
            $signInBtn.before(`<a href="/account/" class="list-group-item list-group-item-action">${data.username}</a><button id="sign-out" data-action="sign-out" class="list-group-item list-group-item-action">Sign out</button>`);
            $signInBtn.css('display', 'none');
            // Hide file nav login and show open saved link
            $('#file-nav .hide').removeClass('hide');
            $('#subnav-sign-in-modal').addClass('hide');
            // Hide top nav login and create account button
            $('#sign-in-modal-2').before(`<a href="/account/" class="btn btn-link account-action">${data.username}</a>`);
            $('#sign-in-modal-2').css('display', 'none');
        }
    },
};

main.utils = {
    arrayToHtmlList: (arr, listID) =>
      arr.map(item => (document.querySelector('#' + listID).innerHTML += `<li>${item}</li>`))
};
