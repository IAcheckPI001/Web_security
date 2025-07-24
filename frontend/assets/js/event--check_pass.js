
const pass_8 = document.getElementById('pass_8');
const pass_acsii = document.getElementById('pass_acsii');
const pass_special = document.getElementById('pass_special');

const pass_8_ico = document.getElementById('pass_8-ico');
const pass_acsii_ico = document.getElementById('pass_acsii-ico');
const pass_special_ico = document.getElementById('pass_special-ico');

const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirm--password');
const registerButton = document.getElementById('btn--sigup__verify');


function removeDiacritics(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}
let check1 = false;
let check2 = false;
let check3 = false;

passwordInput.addEventListener('input', function() {

    if (passwordInput.value.length > 12) {
        pass_8.style.color = "black";
        pass_8_ico.style.display = "block";
        check1 = true;
    } else {
        pass_8.style.color = "rgb(141, 141, 141)";
        pass_8_ico.style.display = "none";
        check1 = false;
    }

    if (/[A-Z]/.test(passwordInput.value) && /[a-z]/.test(passwordInput.value) && /[0-9]/.test(passwordInput.value)) {
        pass_acsii.style.color = "black";
        pass_acsii_ico.style.display = "block";
        check2 = true;
    } else {
        pass_acsii.style.color = "rgb(141, 141, 141)";
        pass_acsii_ico.style.display = "none";
        check2 = false;
    }

    var pass_str = removeDiacritics(passwordInput.value)
    if (/[^a-zA-Z0-9]/.test(pass_str)) {
        pass_special.style.color = "black";
        pass_special_ico.style.display = "block";
        check3 = true;
    }else {
        pass_special.style.color = "rgb(141, 141, 141)";
        pass_special_ico.style.display = "none";
        check3 = false;
    }

});


confirmPasswordInput.addEventListener('input', function() {

  if (check1 == true && check2 == true && check3 == true && passwordInput.value === confirmPasswordInput.value) {
    registerButton.style.backgroundColor = "rgb(130, 130, 214)";

    registerButton.disabled = false;
  } else {
    registerButton.style.backgroundColor = "rgb(173 173 218)";
    registerButton.disabled = true;
  }
});

  