window.addEventListener("load", function () {
    // Sign in
    var signInBtn = document.querySelector('.sign-in');
    // Register
    var registerBtn = document.querySelector('#register-form');

    $('#login-modal').on('shown.bs.modal', function(event) {
        if (signInBtn) {
            signInBtn.addEventListener('submit', function(event) {
                event.preventDefault();
                main.auth.signIn(event, this);
            });
        }
        if (registerBtn) {
            registerBtn.addEventListener('submit', function(event) {
                event.preventDefault();
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
                        main.auth.success(response);
                    } else {
                      main.auth.failure(response);
                    }
                },
                error: function(response) {
                    main.auth.failure(response);
                }
            })
        },
        logOut: function() {
            $.ajax({
                url: '/account/logout_async/',
                success: function (response) {
                    document.location.reload();
                },
                error: function(response) {
                    alert("Unknown error while signing out. Please try again.")
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
                    if (response.success === true) {
                        main.auth.success(response);
                    } else {
                        main.auth.failure(response);
                    }
                },
                error: function(response) {
                    alert('Unknown error occurred: ' + response);
                }
            })
        },
        success: function(data) {
            var docLocation = document.location.pathname;
            // set new csrf token'
            if (docLocation.includes('app')) {
                csrftoken = getCookie('csrftoken');
                if (app) {
                    $('#nav-load-save').removeClass('hide');
                    $('#subnav-sign-in-modal').addClass('hide');
                    $('#upload-treatment-form input[name="csrfmiddlewaretoken"]').val(csrftoken);
                }
            }
            $('#login-modal').modal('hide');
            // show alert
            $('#login-success-username').html(data.username);
            $('#login-success-modal').css('visibility','visible');
            $('#login-success-modal').addClass('show');
            setTimeout(function(){
              $('#login-success-modal').removeClass('show');
              setTimeout(function(){
                $('#login-success-modal').css('visibility','hidden');
              },150)
            }, 4000)

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
            if (app.state.scenarioId) {
              $.ajax({
                url: '/ucsrb/claim_treatment_area/',
                data: {
                    scenario: app.state.scenarioId,
                },
                dataType: 'json',
                success: function(response) {
                      if (response.status != 'Success') {
                        var message = `Error (${response.code}): ${response.message} Unable to reset ownership of current proposed treatment. You will need to start over to save this to your account to view later.`
                        alert(message);
                      }
                },
                error: function(response) {
                    var message = `Error (${response.code}): ${response.message}. Unable to reset ownership of current proposed treatment. You will need to start over to save this to your account to view later.`
                    alert(message);
                }
              })
            }
        },
        failure: function(data) {
          $('#login-failure-modal').css('visibility','visible');
          $('#login-failure-modal').addClass('show');
        }
    },
};

main.utils = {
    arrayToHtmlList: (arr, listID) =>
      arr.map(item => (document.querySelector('#' + listID).innerHTML += `<li>${item}</li>`))
};
