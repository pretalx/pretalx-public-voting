document.addEventListener('DOMContentLoaded', () => {
  const shareButtons = document.querySelectorAll("a[data-pretalx-voting-selector='share']")
  const successTextAttributeName = "data-pretalx-voting-copied-successful-text"

  shareButtons.forEach((button) => {
    const resetHTML = button.innerHTML; // Ensures that original text is always restored even if button is pressed multiple times.
    button.addEventListener('click', async (event) => {
      event.preventDefault();
      const votingPath = button.getAttribute("href");
      const successText = button.getAttribute(successTextAttributeName);
      if (votingPath === null) return console.error('Share button clicked but no URL found.', { button });
      const link = window.location.origin + votingPath;
      navigator.clipboard.writeText(link)
        .then(() =>  button.textContent = successText ?? 'Copied!') // Falling back to english translation just in case.
        .catch((error) => console.error('Failed to copy url to clipboard', { link, error, button }))
        .finally(() => setTimeout(() => button.innerHTML = resetHTML, 3000));
    })
  })
})
