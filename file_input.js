function handleFiles(files) {
    document.getElementById('files').innerHTML = "";
    files = [...files]
    files.forEach(loadFile)
}

function loadFile(file) {
    let reader = new FileReader()
    if (file.name.slice(-4).toLowerCase() === '.zip') {
	reader.readAsArrayBuffer(file)
    } else if (file.name.slice(-4).toLowerCase() == '.hy3') {
	reader.readAsBinaryString(file)
    }
    
    reader.onloadend = function() {
	let div = document.createElement('div')
	let p_name = document.createElement('p')
	p_name.innerText = file.name
	div.appendChild(p_name)
	let p_md5 = document.createElement('p')
	if (file.name.slice(-4).toLowerCase() === '.zip') {
	    p_md5.innerText = "md5: " + CryptoJS.MD5(CryptoJS.lib.WordArray.create(reader.result))
	} else if (file.name.slice(-4).toLowerCase() == '.hy3') {
	    p_md5.innerText = "md5: " + CryptoJS.MD5(reader.result)
	}
	div.appendChild(p_md5)
	let hidden_file = document.createElement('hidden')
	hidden_file.id = "file_contents"
	hidden_file.value = reader.result
	div.appendChild(hidden_file)
	document.getElementById('files').appendChild(div)
  }
}

