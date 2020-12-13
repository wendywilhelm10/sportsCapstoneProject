addSport = document.getElementById('addSport');
addLeague = document.getElementById('addLeague');
saveNote = document.getElementById('saveNote');
$('.delete-team').click(deleteTeam);

addSport.addEventListener('click', function(e) {
    const sport_name = $('#sport option:selected').text();
    document.getElementById('sportName').value = sport_name;
});

addLeague.addEventListener('click', function(e) {
    const league_name = $('#league option:selected').text();
    document.getElementById('leagueName').value = league_name;
});

async function deleteTeam() {
    const id = $(this).data('ut')
    res = await axios.delete(`/api/team/${id}`)
    $(this).parent().parent().parent().parent().remove()
}

saveNote.addEventListener('click', async function(e) {
    const id = $(this).data('id')
    notes = document.getElementById('ta').value
    res = await axios.post(`/api/save/${id}`, {notes: notes})
    if (res.data === 'saved') {
        alert('Save was successful')
    } else {
        alert('Something went wrong.  Data was not saved.')
    }
})
