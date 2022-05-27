document.colorForm.onclick = function() {
    let radio = document.querySelector('input[name = colors]:checked').value;
    change_color(radio);
}





function change_color(value) {
    switch (value) {
        case "blue":
            title.style.backgroundColor = '#537fbe';
            console.log("1");
            break;
            case "black":
            title.style.backgroundColor = '#191919';
            break;
            case "green":
            title.style.backgroundColor = '#84a98e';
            break;
            case "orange":
            title.style.backgroundColor = '#faa275';
            break;
            case "pink":
            title.style.backgroundColor = '#fbb3c0';
            break;
            case "purple":
            title.style.backgroundColor = '#9873ac';
            break;
            case "red":
            title.style.backgroundColor = '#ce4257';
            break;
            case "yellow":
            title.style.backgroundColor = '#e9c46a';
            break;
        default:
            title.style.backgroundColor = '#537fbe';   
            console.log("2");   
    }
}

change_color();