window.persona_email = window.persona_email || null;

window.onload = function() {

    var onDelete = deleteHandler(deleteComplete, deleteError);
    var onLogin = loginHandler(loginComplete, loginError);
    var onLogout = signoutHandler(logoutComplete, logoutError);

    bind_link('persona', function(id) { id.request(); });
    if (window.persona_email) {
        bind_link('logout', function(id) { id.logout(); });
        bind_link('delete', onDelete);
    }

    navigator.id.watch({
        loggedInUser: window.persona_email,
        onlogin: onLogin,
        onlogout: onLogout });

    function loginComplete() {
        addFlashMessage('Persona verified, redirecting');
        redirect_url = getParameterByName('next');
        if (redirect_url) {
            window.location = redirect_url;
        } else {
            window.location.reload();
        }
    }

    function deleteComplete() {
        navigator.id.logout();
    }

    function logoutComplete() {
        window.location.reload();
    }

    function loginError(xhr) {
        addFlashMessage('Error logging in Persona');
    }

    function logoutError(xhr) {
        addFlashMessage('Error logging with Persona');
    }

    function deleteError(xhr) {
        navigator.id.logout();
        addFlashMessage('Error deleting account');
    }

    function addFlashMessage(message) {
        p = document.createElement('p');
        p.className = "message";
        p.innerText = message;
        message = document.getElementById('messages');
        message.appendChild(p);
    }

    function bind_link(id,done) {
        var element = document.getElementById(id);
        if (element) {
            element.onclick = function() {
                return done(navigator.id) || false;
            };
        };
    }

    function getParameterByName(name) {
        var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
        return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
    }

    function xhrCallback(xhr, success, error) {
        return function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200){
                    success(xhr);
                }
                else {
                    error(xhr);
                }
            }
        }
    }

    function deleteHandler(success, error) {
        return function() {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/authentication/", true);
            xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhr.send("delete=Delete account");
            xhr.onreadystatechange = xhrCallback(xhr, success, error);
        }
    }

    function loginHandler(success, error) {
        return function(assertion) {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/authentication/persona", true);
            xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhr.send("assert=" + assertion);
            xhr.onreadystatechange = xhrCallback(xhr, success, error);
        }
    }

    function signoutHandler(success, error) {
        return function() {
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/authentication/logout", true);
            xhr.send(null);
            xhr.onreadystatechange = xhrCallback(xhr, success, error);
        }
    }
}
