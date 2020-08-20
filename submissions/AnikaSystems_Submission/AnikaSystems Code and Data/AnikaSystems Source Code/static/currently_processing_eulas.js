/* currently_processing_eulas.js - Render table that show eulas currently being parsed and ran through classifier. */

$(document).ready(function() {
    console.log("Processing table init.");
    $('#documents-processing').footable();
});


/* Retrieve db data every 3 seconds. */
get_queue_data();
setInterval(function() {
    get_queue_data();
}, 3000);


function get_queue_data() {
    /* Retrieve data in the queue and render it to the table. */
    /* TODO: Fill in. */
    $.get("/queue_files", function(vresp) {
        vresp = JSON.parse(vresp);
        //console.log("[*] Queue response: ", vresp);
        let vqueue_html = "";

        for(let vitem of vresp) {
            let vtime = vitem["upload_time"];
            vtime = formatDate(vtime);

            /*let vavg_accuracy = average_accuracy(vitem["clauses"])
            let vavg_label = "";
            if(vavg_accuracy > 79) vavg_label = "text-success";
            else if(vavg_accuracy > 59) vavg_label = "text-warning";
            else vavg_label = "text-danger";*/ 

            /* Alert if document has finished processing. */
            console.log(vitem["completed"]);
            if(vitem["completed"] == 100) {
                toastr.success(`${vitem["fname"]} has finished processing.`);
            }

            let vprogress = `
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated progress-bar-info" 
                     style="width: ${vitem["completed"].toString()}%" 
                     role="progressbar" 
                     aria-valuenow="${vitem["completed"].toString()}" 
                     aria-valuemin="0" 
                     aria-valuemax="100"></div>
            </div>
            `
            /* Create filename HTML. */
            let vfname_html = "";
            let vext = vitem["fname"].split(".").pop().toUpperCase();            
            if(vext == "PDF") {
                vfname_html = `<p><i style="color:red;" class="fa fa-file-pdf-o"></i>&nbsp;&nbsp;<a href="#">${vitem["fname"]}</a></p>`;

            } else if(vext == "DOCX") {
                vfname_html = `<p><i style="color:blue;" class="fa fa-file-word-o"></i>&nbsp;&nbsp;<a href="#">${vitem["fname"]}</a></p>`;
            }

            vqueue_html += `
                <tr class="gradeX">
                <td>${vfname_html}</td>
                <td class="text-center text-info">${vprogress}</td>
                <td class="text-center">${vtime}</td>

                <!--td class="text-center text-danger">${((vitem["fsize"] / 1024) / 1024).toFixed(2).toString() + " MB"}</td-->
                </tr>
                `;
        }
        
        if(vresp.length == 0) {
            $("#table-empty-documents-processing").fadeIn("slow");
        } 
        else {
            $("#table-empty-documents-processing").fadeOut("slow", function() {
                $("#table-empty-documents-processing").hide();
            });
        }

        setTimeout(function() {
            $('#documents-processing-body').html(vqueue_html);
            $("#documents-processing").trigger('footable_redraw');
        }, 1300);

    });
}


function formatDate(date) {
    var d = new Date(date);
    var hh = d.getHours();
    var m = d.getMinutes();
    var s = d.getSeconds();
    var dd = "AM";
    var h = hh;
    if (h >= 12) {
        h = hh - 12;
        dd = "PM";
    }
    
    if (h == 0) h = 12;
    m = m < 10 ? "0" + m : m;
    s = s < 10 ? "0" + s : s;
  
    /* if you want 2 digit hours:
    h = h<10?"0"+h:h; */
  
    var pattern = new RegExp("0?" + hh + ":" + m + ":" + s);
  
    var replacement = h + ":" + m;
    /* if you want to add seconds
    replacement += ":"+s;  */
    replacement += " " + dd;

    let vd = d.toISOString().split("T")[0].split("-");
    let vdate = vd[1] + "-" + vd[2] + "-" + vd[0];
  
    return `${vdate} @ ${replacement}`;
}