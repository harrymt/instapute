
function main() {
	setTimeout(function () {
		if (window.location.pathname.indexOf('render') > 0 && document.getElementById("completed").value == "False") {
			window.location = window.location;
		} else {
			console.log("Completed render!");
		}
	}, 5000);
}



main();
