function rm_check(event) {
    if (event.target.project_name.value === '') {
        alert("No name for project specified");
        event.preventDefault();
        return false;
    }
    if (!event.target.remove.checked) {
        alert("Accept Checkbox to remove project");
        event.preventDefault();
        return false;
    }
}

function rn_check(event) {
    if (event.target.project_name_old.value === '' || event.target.project_name_new.value === '') {
        alert("No name for project specified");
        event.preventDefault();
        return false;
    }
    if (event.target.project_name_new.value.includes(" ")){
        alert("Avoid space in the project names! Use '_' instead")
        event.preventDefault();
        return false;
    }

}

function add_check(event) {
    console.log(event.target.project_name.value.includes(" "))
    if (event.target.project_name.value === '') {
        alert("No name for project specified");
        event.preventDefault();
        return false;
    }

    if (event.target.project_name.value.includes(" ")){
        alert("Avoid space in the project names! Use '_' instead")
        event.preventDefault();
        return false;
    }
}