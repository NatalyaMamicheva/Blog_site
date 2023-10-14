function commentReplyToggle(parent_id) {
    console.log('скрипт заработал')
    const row = document.getElementById(parent_id);
    if (row.classList.contains('d-none')) {
        row.classList.remove('d-none');
    } else {
        row.classList.add('d-none');
    }
}