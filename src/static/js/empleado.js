const slidePage = document.querySelector(".slide-page");
const nextBtnFirst = document.querySelector(".firstNext");
const prevBtnSec = document.querySelector(".prev-1");
const nextBtnSec = document.querySelector(".next-1");
const prevBtnThird = document.querySelector(".prev-2");
const nextBtnThird = document.querySelector(".next-2");
const prevBtnFourth = document.querySelector(".prev-3");
const submitBtn = document.querySelector(".submit");
const progressText = document.querySelectorAll(".step p");
const progressCheck = document.querySelectorAll(".step .check");
const bullet = document.querySelectorAll(".step .bullet");
let current = 1;

function validarSelect() {
  var selects = document.querySelectorAll(".page.f1 select[required]");
  var isValid = true;
  for (var i = 0; i < selects.length; i++) {
    if (!selects[i].value.trim()) {
      isValid = false;
      mostrarMensajeError("Por favor, completa todos los campos requeridos.");
      break;
    }
  }
  if (isValid) {
    ocultarMensajeError();
  }
  return isValid;
}

function validarSelect2() {
  var selects = document.querySelectorAll(".page.f2 select[required]");
  var isValid = true;
  for (var i = 0; i < selects.length; i++) {
    if (!selects[i].value.trim()) {
      isValid = false;
      mostrarMensajeError("Por favor, completa todos los campos requeridos.");
      break;
    }
  }
  if (isValid) {
    ocultarMensajeError();
  }
  return isValid;
}

var errorMessage = document.querySelector(".error-message");
var errorMessage2 = document.querySelector(".error-message2");
var errorMessage3 = document.querySelector(".error-message3");
var errorMessage4 = document.querySelector(".error-message4");

function validarInputs() {
  var inputs = document.querySelectorAll(".page.slide-page input[required]");
  var isValid = true;
  for (var i = 0; i < inputs.length; i++) {
    if (inputs[i].value.trim() === '') {
      isValid = false;
      mostrarMensajeError("Por favor, completa todos los campos requeridos.");
      break;
    }
  }
  if (isValid) {
    ocultarMensajeError();
  }
  return isValid;
}

function validarInputs2() {
  var inputs = document.querySelectorAll(".page.f1 input[required]");
  var selects = document.querySelectorAll(".page.f1 select[required]");
  var isValid = true;
  for (var i = 0; i < inputs.length; i++) {
    if (inputs[i].value.trim() === '') {
      isValid = false;
      mostrarMensajeError("Por favor, completa todos los campos requeridos.");
      break;
    }
  }
  if (isValid) {
    isValid = validarSelect(); // Validar los campos <select>
  }
  if (isValid) {
    ocultarMensajeError();
  }
  return isValid;
}

function validarInputs3() {
  var inputs = document.querySelectorAll(".page.f2 input[required]");
  var selects = document.querySelectorAll(".page.f2 select[required]");
  var isValid = true;
  for (var i = 0; i < inputs.length; i++) {
    if (inputs[i].value.trim() === '') {
      isValid = false;
      mostrarMensajeError("Por favor, completa todos los campos requeridos.");
      break;
    }
  }
  if (isValid) {
    isValid = validarSelect(); // Validar los campos <select>
  }
  if (isValid) {
    ocultarMensajeError();
  }
  return isValid;
}

function validarInputs4() {
  var inputs = document.querySelectorAll(".page.f3 input[required]");
  var isValid = true;
  for (var i = 0; i < inputs.length; i++) {
    if (inputs[i].value.trim() === '') {
      isValid = false;
      mostrarMensajeError("Por favor, completa todos los campos requeridos.");
      break;
    }
  }
  if (isValid) {
    ocultarMensajeError();
  }
  return isValid;
}

function mostrarMensajeError(mensaje) {
  errorMessage.textContent = mensaje;
  errorMessage.style.display = "block";
  errorMessage2.textContent = mensaje;
  errorMessage2.style.display = "block";
  errorMessage3.textContent = mensaje;
  errorMessage3.style.display = "block";
  errorMessage4.textContent = mensaje;
  errorMessage4.style.display = "block";
}

function ocultarMensajeError() {
  errorMessage.textContent = "";
  errorMessage.style.display = "none";
  errorMessage2.textContent = "";
  errorMessage2.style.display = "none";
  errorMessage3.textContent = "";
  errorMessage3.style.display = "none";
  errorMessage4.textContent = "";
  errorMessage4.style.display = "none";
}

nextBtnFirst.addEventListener("click", function(event){
  event.preventDefault();
  if (validarInputs()) {
    slidePage.style.marginLeft = "-25%";
    bullet[current - 1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
    current += 1;}
});
nextBtnSec.addEventListener("click", function(event){
  event.preventDefault();
  if (validarInputs2() && validarSelect()) {
    slidePage.style.marginLeft = "-50%";
    bullet[current - 1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
    current += 1;
  }
});
nextBtnThird.addEventListener("click", function(event){
  event.preventDefault();
  if (validarInputs3() && validarSelect2()) {
    slidePage.style.marginLeft = "-75%";
    bullet[current - 1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
    current += 1;}
});
submitBtn.addEventListener("click", function(){
  if (validarInputs4()) {
    bullet[current - 1].classList.add("active");
    progressCheck[current - 1].classList.add("active");
    progressText[current - 1].classList.add("active");
    current += 1;
    setTimeout(function(){
      alert("Te has registrado correctamente");
    },);
  }
});

prevBtnSec.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "0%";
  bullet[current - 2].classList.remove("active");
  progressCheck[current - 2].classList.remove("active");
  progressText[current - 2].classList.remove("active");
  current -= 1;
});
prevBtnThird.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "-25%";
  bullet[current - 2].classList.remove("active");
  progressCheck[current - 2].classList.remove("active");
  progressText[current - 2].classList.remove("active");
  current -= 1;
});
prevBtnFourth.addEventListener("click", function(event){
  event.preventDefault();
  slidePage.style.marginLeft = "-50%";
  bullet[current - 2].classList.remove("active");
  progressCheck[current - 2].classList.remove("active");
  progressText[current - 2].classList.remove("active");
  current -= 1;
});

  var cedulaInput = document.getElementById("documento");
  var cedulaError = document.getElementById("cedulaError");

    cedulaInput.addEventListener("input", function(event) {
      var cedula = event.target.value;

      // Realizar petición Ajax al backend para validar la cédula
      fetch('/validar-cedula', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cedula: cedula })
      })
      .then(response => response.json())
      .then(data => {
        if (data.existeDocumento) {
          cedulaError.textContent = "Documento ya existe";
        } else {
          cedulaError.textContent = "";
        }
      })
      .catch(error => {
        console.error('Error al realizar la petición:', error);
      });
    });



