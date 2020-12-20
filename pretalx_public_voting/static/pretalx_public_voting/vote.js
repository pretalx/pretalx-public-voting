'use strict'

let voteDirty = false;

$(() => {
  const csrftoken = getCookie("pretalx_csrftoken")
  const saveIndicator = $("#js-save")
  const saving = saveIndicator.children(".badge-primary")
  const saved = saveIndicator.children(".badge-success")

  $('label').on('click', (event) => {
    $(".fa-spin").removeClass("d-none")
    saved.addClass("invisible")
    saving.removeClass("invisible")
    window.setTimeout(() => {
      const form = $("form")
      $.post(form.attr('action'), form.serialize(), function(res){
          $(".fa-spin").addClass("d-none")
          saved.removeClass("invisible")
          saving.addClass("invisible")
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
