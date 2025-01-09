document.addEventListener('DOMContentLoaded', () => {
  const saveIndicator = document.querySelector("#js-save")
  const saving = saveIndicator.querySelector(".pretalx-vote-badge-primary")
  const saved = saveIndicator.querySelector(".pretalx-vote-badge-success")
  const savingSpinner = document.querySelector(".fa-spin")
  const form = document.querySelector("form")

  document.querySelectorAll('input[type="radio"]').forEach((input) => {
    input.addEventListener('change', (event) => {
      savingSpinner.classList.remove("d-none")
      saved.classList.add("d-none")
      saving.classList.remove("d-none")
      window.setTimeout(() => {
          fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
          }).then((res) => {
            savingSpinner.classList.add("d-none")
            saved.classList.remove("d-none")
            saving.classList.add("d-none")
          })
      }, 5)
    })
  })
})
