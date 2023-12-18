function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

const nameDropdown = document.getElementById('nameDropdown');
    const selectedName = document.getElementById('selectedName');
  
    nameDropdown.addEventListener('change', function() {
      selectedName.textContent = nameDropdown.value;
    });