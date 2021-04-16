/**
 * Retrieves the iframe which is the next sibling element of the clicked button (a)
 * and set its src attribute so that it starts loading only at this moment
 * 
 * @param {HTMLAnchorElement} a The a element that has been clicked
 */
function load(a) {
    iframe = a.nextElementSibling; //Because in HTMl order, the next element is the iframe
    iframe.setAttribute('src', iframe.getAttribute('data-value'));

    a.style.display = "none";
}