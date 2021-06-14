const getFormJSON = () => {
  var form = document.querySelector("form");
  event.preventDefault();
  const data = new FormData(form);
  return Array.from(data.keys()).reduce((result, key) => {
    result[key] = parseInt(data.get(key));
    return result;
  }, {});
};

const saveText = (data, filename = "bad") => {
  var blob = new Blob([data], { type: "text/plain;charset=utf-8;" });
  var elem = window.document.createElement("a");
  elem.href = window.URL.createObjectURL(blob);
  elem.download = `${filename}.cs`;
  document.body.appendChild(elem);
  elem.click();
  document.body.removeChild(elem);
};

const generate = () => {
  var out = [
    "# ARTICULOS	HUMANOS TOTAL	BLOQUES	SALONES	TRACKS	ARTICULOS POR SESION	SESIONES POR DIA",
  ];
  const { nA, nP, nR, nB, nAS, nT } = getFormJSON();

  out.push([nA, nP, nR, nB, nAS, nT].join(" "));

  saveText(out.join("\n"), [nA, nP, nR, nB, nAS, nT].join("-"));
};
