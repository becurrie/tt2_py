/**
 * login.js
 *
 * Handle functionality related to the authentication of users before being able to access
 * the titandash dashboard system.
 *
 * Ajax handles the submit request to allow for some additional loading functionality.
 *
 * Models are present to preserve the information entered by the user. They will stay logged in
 * as long as they wish, until they decide to logout.
 */
$(document).ready(function() {
    return new LoginHandler();
});

/**
 * LoginHandler function contains all functions used to grab data and authenticate user information entered.
 */
function LoginHandler() {
    let ajaxOptions = {
        url: "/auth/ajax/credentials",
        type: "POST",
        dataType: "JSON"
    };
    let redirectUrl = "/bootstrap";

    // Loader template used to display a moving icon while a request is being processed
    // through an AJAX request.
    let loaderTemplate =
        `
        <div class="w-100 d-flex justify-content-center align-items-center loader-template" style="display: none;">
            <div class="spinner">
                <div class="rect1"></div>
                <div class="rect2"></div>
                <div class="rect3"></div>
                <div class="rect4"></div>
                <div class="rect5"></div>
            </div>      
        </div>
        `;

    // Login form elements used through implementation.
    let elements = {
        loginForm: $(".form-signin"),
        loginEmail: $("#inputEmail"),
        loginToken: $("#inputToken"),
        loginSignIn: $("#signInButton"),
        loginSignUp: $("#signUpButton"),
        loaderContainer: $("#loaderContainer"),
        messageContainer: $("#messageContainer")
    };

    /**
     * Setup the login form to prevent the normal form submit flow.
     *
     * Using a custom flow to allow ajax to authenticate our credentials and provide
     * some feedback to determine if the entered credentials are valid.
     */
    this.setupLoginForm = function() {
        let _this = this;
        elements.loginForm.submit(function(event) {
            // Preventing default form submit. Handling through ajax calls
            // to determine successful/un-successful login.
            event.preventDefault();

            // Perform ajax request to authenticate user credentials.
            _this.performAjax();
        });
    };

    this.performAjax = function() {
        let _this = this;

        // Perform jQuery AJAX.
        $.ajax({
            url: ajaxOptions.url,
            type: ajaxOptions.type,
            dataType: ajaxOptions.dataType,
            data: elements.loginForm.serializeArray(),
            beforeSend: _this.beforeSendCallback,
            success: _this.successCallback,
            error: _this.errorCallback,
            complete: _this.completeCallback
        });
    };

    /**
     * jQuery AJAX beforeSend callback.
     */
    this.beforeSendCallback = function(jqXHR, settings) {
        // Disable all inputs and display a loader icon.
        elements.loginEmail.prop("disabled", true);
        elements.loginToken.prop("disabled", true);
        elements.loginSignIn.prop("disabled", true);
        elements.loginSignUp.prop("disabled", true);
        elements.loginForm.fadeTo(100, 0.5, null, function() {
            // Display loader.
            $(loaderTemplate).appendTo(elements.loaderContainer).fadeIn(100);
        });
    };

    /**
     * jQuery AJAX success callback.
     */
    this.successCallback = function(data, textStatus, jqXHR) {
        if (data.status === "success") {
            for (let elem in elements)
                elements[elem].fadeOut(50);

            // Redirect the user to the main index page.
            window.location = redirectUrl;
        }

        if (data.status === "error") {
            sendAlert(data.message, elements.messageContainer, null, "danger", false, true);
        }
    };

    /**
     * jQuery error callback.
     */
    this.errorCallback = function(jqXHR, textStatus, errorThrown) {
        sendAlert(textStatus, elements.messageContainer, null, "danger", false, true);
    };

    /**
     * jQuery complete callback.
     */
    this.completeCallback = function(jqXHR, textStatus) {
        // Enable inputs again.
        elements.loginEmail.prop("disabled", false);
        elements.loginToken.prop("disabled", false);
        elements.loginSignIn.prop("disabled", false);
        elements.loginSignUp.prop("disabled", false);
        elements.loginForm.fadeTo(100, 1, null, function() {
            // Remove loader.
            elements.loaderContainer.find(".loader-template").fadeOut(100, function() {
                $(this).remove();
            });
        });
    };

    // Main.
    this.setupLoginForm();
}