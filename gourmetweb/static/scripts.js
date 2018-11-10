function visualizeCheck(checkboxElem) {
  var elements = document.getElementsByName(checkboxElem.name);
  for (var i = 0; i < elements.length; i++ ) {
    if (checkboxElem.checked) {
      elements[i].style.color = '#aaa';
    } else {
      elements[i].style.color = '#000';
    }
  }
}
