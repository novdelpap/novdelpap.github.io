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
  var files = dt.files

  handleFiles(files)
}

function handleFiles(files) {
    files = [...files]
    console.log("handle files")
    console.log(files)
  files.forEach(previewFile)
}

function previewFile(file) {
    console.log("preview file")
    console.log(file)
  let reader = new FileReader()
  reader.readAsBinaryString(file)
    reader.onloadend = function() {
	console.log("onloadend")
	let p = document.createElement('p')
	console.log("created p")
      //img.src = reader.result
	p.innerText = file
	console.log("added " + file + " to p")
	p.innerText += " "
	p.innerText += CryptoJS.MD5(reader.result)
	console.log("added md5, now: " + p.innerText)
	document.getElementById('gallery').appendChild(p)
	console.log("gallery should now have " + document.getElementById('gallery').length + " children")
  }
}

