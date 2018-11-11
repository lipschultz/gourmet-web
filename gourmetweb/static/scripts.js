function visualizeCheck(checkboxElem) {
  var elements = document.getElementsByName(checkboxElem.name);
  for (var i = 0; i < elements.length; i++ ) {
    if (checkboxElem.checked) {
      if (elements[i].classList.contains('optional')) {
        elements[i].classList.add('optional-complete');
      } else {
        elements[i].classList.add('complete');
      }
    } else {
      if (elements[i].classList.contains('optional-complete')) {
        elements[i].classList.remove('optional-complete');
      } else {
        elements[i].classList.remove('complete');
      }
    }
  }
}
