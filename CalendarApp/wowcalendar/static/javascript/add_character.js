const select1 = document.querySelector('#class');
const select2 = document.querySelector('#specialization');

var fixed_list = python_list.replace(/&#x27;/g,'\"');
var final_dict = String(fixed_list)
var numList

function getNumFromStr () {
  numString = String((final_dict.match(/\d+/g)))
  numList = numString.split(",");
  return numList
}

numList = getNumFromStr()
var final_dict = String(fixed_list)

for (let i = 0; i < numList.length; i++) {

  let inputString = final_dict;
  let replaceThis = String(numList[i]);
  let re = new RegExp(`\\b${replaceThis}\\b`, 'gi');
  let replaceString = '\"' + String(numList[i]) + '\"'

  final_dict = inputString.replace(re, replaceString)
}

//Dictionary of keys and list of specs per class
const json_specs = JSON.parse(final_dict)


select1.addEventListener('change', function() {

  currentClassPK = this.value
  var specList = json_specs[currentClassPK]

  let innerHtml = '';
  specList.forEach((spec) => {
    innerHtml += `<option value=${spec} selected>${spec}</option>`;
  });

  select2.innerHTML = innerHtml

});