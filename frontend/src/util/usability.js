export default function copyToClipboard (text) {
  // Create an element with position -9999 px, focus it's content, copy the content, remove it
  const el = document.createElement('textarea')
  el.value = text
  el.setAttribute('readonly', '')
  el.style = {
    position: 'absolute',
    left: '-9999px'
  }
  document.body.appendChild(el)
  el.select()
  document.execCommand('copy')
  document.body.removeChild(el)
}
