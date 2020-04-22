'use strict'

let voteDirty = false;
let submitButton = null;

$(() => {
  const csrftoken = getCookie("pretalx_csrftoken")
  submitButton = $("#save-bar button")
  submitButton.prop("disabled", true)

  $('label').on('click', (event) => {
    submitButton.prop("disabled", false)
    $(".fa-spin").removeClass("d-none")
    window.setTimeout(() => {
      const form = $("form")
      $.post(form.attr('action'), form.serialize(), function(res){
          submitButton.prop("disabled", true)
          $(".fa-spin").addClass("d-none")
      })
    }, 5)
    return true
  })

})

const getCookie = (name) => {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue;
}
