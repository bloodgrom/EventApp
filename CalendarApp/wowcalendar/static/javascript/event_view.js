function getDateSuffix(date) {
  let suffix = "th";
  let digits = date % 100;
  if (digits < 11 || digits > 13) {
      switch (date % 10) {
          case 1: suffix = "st"; break;
          case 2: suffix = "nd"; break;
          case 3: suffix = "rd"; break;
      }
  }
  return suffix;
}

function getMonth(num) {
  switch (num) {
      case 1: return "January";
      case 2: return "February";
      case 3: return "March";
      case 4: return "April";
      case 5: return "May";
      case 6: return "June";
      case 7: return "July";
      case 8: return "August";
      case 9: return "September";
      case 10: return "October";
      case 11: return "November";
      case 12: return "December";
      default: return "Of the month";
  }
}

var event_date = document.getElementById("date_number").innerHTML
var event_month = document.getElementById("date_month").innerHTML

let suffix = getDateSuffix(event_date);
//let dateWithSuffix = event_date + suffix;

document.getElementById("date_suffix").innerHTML = suffix;

let event_month_text = getMonth(parseInt(event_month))

document.getElementById("date_month").innerHTML = event_month_text;

let day_month = event_date + suffix + " " + event_month_text

document.getElementById("date_small").innerHTML = day_month;

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = "max-content";
    }
  });
}

// var inner_acc = document.getElementsByClassName("header-inner");
// var j;

// for (j = 0; j < inner_acc.length; j++) {
//   inner_acc[j].addEventListener("click", function() {
//     this.classList.toggle("class_header_active");
//     var panel = this.nextElementSibling;

//     if (panel.style.border) {
//       panel.style.border = null;
//     } else {
//       panel.style.border = "1px solid #212121";
//     }
//   });
// }

var inner_panels = document.getElementsByClassName("panel-inner");
var k;

for (k = 0; k < inner_panels.length; k++) {
  if (inner_panels[k].innerText == "") {

    insert_before_el = inner_panels[k].children[1]

    var para = document.createElement("p");
    var node = document.createTextNode("----");
    para.appendChild(node);

    para.className = "text-center mb-1 text_italic";

    inner_panels[k].insertBefore(para, insert_before_el);

    //console.log(inner_panels[k].children[2])
  }
  //console.log(k + " - " + inner_panels[k].innerText)
}