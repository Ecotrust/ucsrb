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
            } else if (event.target.dataset.action == 'sign-in-modal-2') {
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
                success: function(response) {
                    if (response.success === true) {
                        console.log('%csuccessfully signed in user', 'color:green;');
                        main.auth.success(response);
                    } else {
                        if (response.username.length > 0) {
                            console.log('%cerror wrong username or password: %o', 'color: red;', response);
                            if ($('.alert').length === 0) {
                                $('#login-collapse .login-form').prepend(`<div class="alert alert-warning fade show" role="alert" style="position: relative; display: block; font-size: .875em;"></div>`);
                            }
                            var $alert = $('.alert');
                            $alert.html(`Password does not match username. Please try again.<br />You may also <a href="/account/forgot/">reset your password</a>. Reseting your password will cause your current progress to be lost.`);
                        }
                        console.log('%cerror with sign in credentials: %o', 'color: red;', response);
                    }
                },
                error: function(response) {
                    console.log('%cerror with sign in request submission: %o', 'color: red', response);
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
            var url = '/account/register_login_async/';
            $.ajax({
                url: url,
                type: 'POST',
                data: formData,
                dataType: 'json',
                success: function (response) {
                    console.log('%csuccessfully registered in user', 'color:green;');
                    if (response.success === true) {
                        main.auth.success(response);
                    } else {
                        document.querySelector('#registration-error').innerHTML = `${response.error}. Please update then submit`;
                    }
                },
                error: function(response) {
                    console.log('%error registering in user', 'color:red;');
                }
            })
        },
        success: function(data) {
            // set new csrf token
            csrftoken = getCookie('csrftoken');
            $('#login-modal').modal('hide');
            if (app) {
              $('#nav-load-save').removeClass('hide');
              $('#subnav-sign-in-modal').addClass('hide');
            }
            // show alert
            $('body').prepend(`<div class="alert alert-success fade show" role="alert" style="position: fixed; top: 10px; left: 50%; transform: translate(-50%,0); min-width: 200px; z-index: 3; text-align: center; font-size: .875em;">SUCCESS</div>`);
            window.setTimeout(function() {
                $('.alert').alert('close');
            }, 1500);
            // menu navicon hide login  &
            // add account link + sign out link
            $('#menu #sign-in-modal').before(`<a href="/account/" class="list-group-item list-group-item-action">${data.username}</a><button id="sign-out" data-action="sign-out" class="list-group-item list-group-item-action">Sign out</button>`);
            $('#menu #sign-in-modal').css('display', 'none');
            // Hide top nav login and create account button
            $('.username-wrap #sign-in-modal-2').before(`<a id="topnav-account-link" href="/account/" class="btn btn-link account-action">
                <i class="svg_icon"><img src="/static/ucsrb/img/icon/i_user_blue.svg" /></i>${data.username}</a>`);
            $('.username-wrap #sign-in-modal-2').css('display', 'none');
            // hide submenu login
            $('#subnav-sign-in-modal').addClass('d-none');
        }
    },
};

main.utils = {
    arrayToHtmlList: (arr, listID) =>
      arr.map(item => (document.querySelector('#' + listID).innerHTML += `<li>${item}</li>`))
};
