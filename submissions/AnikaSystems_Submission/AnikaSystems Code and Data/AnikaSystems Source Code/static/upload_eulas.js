/* upload_eulas.js - Handle file uploads in file input component. */

let VUPLOAD_FILES = [];


$(document).ready(function() {
    console.log("[*] Upload eulas init.");
    install_file_upload();
    /*$('.custom-file-input').on('change', function() {
        console.log($(this).val());

        let fileName = $(this).val().split('\\').pop();
        // $(this).next('.custom-file-label').addClass("selected").html(fileName);
    });*/
});

let VFCOUNTER = 1;

function install_file_upload() {
    /* Install listener for files to be added to array and submitted to server. */

    $("#batch-upload").change(function(e) {
        console.log("[*] Files added!");
        
        /* Grab file names from event. */
        // VUPLOAD_FILES = [];
        let vfiles = e.target.files;
        console.log(vfiles);

        /* Add files to global array and render. */
        for(let i = 0; i < vfiles.length; i++) {
            let vpath = vfiles[i]["name"];
            let vext = vpath.split(".").pop().toUpperCase();            
            let vfname_html = "";

            /* Render by file extension. */
            if(vext == "PDF") {
                vfname_html = `
                <tr>
                    <td>${(VFCOUNTER).toString().padStart(2, "0")}</td>
                    <td>
                        <p><i style="color:red;" class="fa fa-file-pdf-o"></i>&nbsp;&nbsp;${vpath}</p>
                    </td>
                </tr>
                `;
                ++VFCOUNTER;
                VUPLOAD_FILES.push(vfiles[i]);

            } else if(vext == "DOCX") {
                vfname_html = `
                <tr>
                    <td>${(VFCOUNTER).toString().padStart(2, "0")}</td>
                    <td>
                        <p><i style="color:blue;" class="fa fa-file-word-o"></i>&nbsp;&nbsp;${vpath}</p>
                    </td>
                </tr>
                `;
                ++VFCOUNTER;
                VUPLOAD_FILES.push(vfiles[i]);

            } else {
                toastr.error(`The file ${vpath} cannot be uploaded. The file extension ${vext} is not supported.`)
            }

            /* Render file name. */
            if(vfname_html != "") $("#file-names").append(vfname_html);
        }
        

        /* Display or hide empty list text. */
        if(VUPLOAD_FILES.length == 0) {
            $("#file-list-empty").show();
        } else {
            $("#file-list-empty").hide();
        }
    });

    $("#file-uploader").submit(function(e) {
        e.preventDefault();
        if(VUPLOAD_FILES.length == 0) {
            toastr.error(`No files have been selected.`);
        }
        else {
            toastr.success(`${VUPLOAD_FILES.length} EULA's submitted to be checked.`);
        }
        
        VUPLOAD_FILES.forEach(function (vfile) {
            send_file(vfile);
        });
        VUPLOAD_FILES = [];
        VFCOUNTER = 1;
        $("#file-list-empty").show();
        $("#file-names").html("");
    });
}


function send_file(vfile) {
    /* Send a single file to server to be uploaded. */
    let vfdata = new FormData();
    let vreq = new XMLHttpRequest();

    vfdata.set('file', vfile);
    vreq.open("POST", "/process_eula");
    vreq.send(vfdata);
}