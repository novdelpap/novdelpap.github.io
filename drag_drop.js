// ************************ Drag and drop ***************** //
let dropArea = document.getElementById("drop-area")

// Prevent default drag behaviors
;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false)   
  document.body.addEventListener(eventName, preventDefaults, false)
})

// Highlight drop area when item is dragged over it
;['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, highlight, false)
})

;['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, unhighlight, false)
})

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false)

function preventDefaults (e) {
  e.preventDefault()
  e.stopPropagation()
}

function highlight(e) {
  dropArea.classList.add('highlight')
}

function unhighlight(e) {
  dropArea.classList.remove('active')
}

function handleDrop(e) {
    var dt = e.dataTransfer
    console.log("what is this e.dataTransfer? " + e.dataTransfer)
    var files = dt.files
    console.log("handling drop, dt.files has length: " + dt.files.length)
    handleFiles(files)
}

function handleFiles(files) {
    files = [...files]
    console.log("handle files")
    console.log(files)
    files.forEach(loadFile)
}

function loadFile(file) {
    let reader = new FileReader()
    reader.readAsBinaryString(file)
    reader.onloadend = function() {
	let div = document.createElement('div')
	let p_name = document.createElement('p')
	p_name.innerText = file.name
	div.appendChild(p_name)
	let p_md5 = document.createElement('p')
	p_md5.innerText = CryptoJS.MD5(reader.result)
	div.appendChild(p_md5)
	let hidden_file = document.createElement('hidden')
	hidden_file.id = "file_contents"
	hidden_file.value = reader.result
	div.appendChild(hidden_file)
	document.getElementById('files').appendChild(div)
  }
}

