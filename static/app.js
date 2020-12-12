addSport = document.getElementById('addSport');
addLeague = document.getElementById('addLeague');
saveNote = document.getElementById('saveNote');
$('.delete-team').click(deleteTeam);

addSport.addEventListener('click', function(e) {
    console.log('in sport.js click event');
    const sport_name = $('#sport option:selected').text();
    console.log('sport name ', sport_name);
    document.getElementById('sportName').value = sport_name;
});

addLeague.addEventListener('click', function(e) {
    console.log('in click for league name');
    const league_name = $('#league option:selected').text();
    console.log('league name ', league_name);
    document.getElementById('leagueName').value = league_name;
});

async function deleteTeam() {
    const id = $(this).data('ut')
    console.log('id ', id)
    res = await axios.delete(`/api/team/${id}`)
    print('response from axios ', res)
    $(this).parent().parent().parent().parent().remove()
}

saveNote.addEventListener('click', async function(e) {
    const id = $(this).data('id')
    notes = document.getElementById('ta').value
    res = await axios.post(`/api/save/${id}`, {notes: notes})
    console.log(res.data)
    if (res.data === 'saved') {
        alert('Save was successful')
    } else {
        alert('Something went wrong.  Data was not saved.')
    }
})
