document.getElementById("convert").addEventListener("click", function(e) {
  
  const data = { video_url:  document.getElementsByName('video_url')[0].value };

  fetch('http://127.0.0.1:8080/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`The endpoint returned an error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => {
    console.log(data);
    document.getElementById('convert_error').classList.add('is-hidden');
    document.getElementById('convert_success').classList.remove('is-hidden');
    document.getElementById('mp3_download_link').setAttribute('href', `/download-music/${data.data.filename}`);
  })
  .catch((error) => {
    console.error(error);
    document.getElementById('convert_success').classList.add('is-hidden');
    document.getElementById('convert_error').classList.remove('is-hidden');
  });
});