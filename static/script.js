let show = document.querySelectorAll(".show");



for (let i = 0; i < show.length; i++) {
    show[i].addEventListener("click", () => {
        myFunction(show[i].value);
    });
}

function myFunction(value) {
    console.log(value);
    let obj = JSON.stringify(events)
    obj = JSON.parse(obj);
    console.log(obj);
    document.getElementById("info").innerHTML = value;
}

