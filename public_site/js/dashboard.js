const $ = (id) => document.getElementById(id)

let droppedFile = null

function toast(type, message) {
  const wrap = $("toastWrap")
  if (!wrap) return

  const el = document.createElement("div")
  el.className = "toast " + (type || "info")
  const icon = type === "good" ? "ri-check-line" : type === "bad" ? "ri-error-warning-line" : "ri-information-line"
  el.innerHTML = `<div class="row"><div class="ic"><i class="${icon}"></i></div><div class="msg">${message}</div></div>`
  wrap.appendChild(el)

  setTimeout(() => {
    el.style.opacity = "0"
    el.style.transform = "translateY(-6px)"
    el.style.transition = "250ms"
  }, 2800)

  setTimeout(() => el.remove(), 3200)
}

function goLogin() {
  window.location.href = "/site/login.html"
}

function setBusy(isBusy) {
  const btn = $("submitBtn")
  const btnText = $("btnText")
  const btnIcon = $("btnIcon")
  if (!btn || !btnText || !btnIcon) return

  btn.disabled = isBusy
  if (isBusy) {
    btnIcon.innerHTML = `<span class="loader"></span>`
    btnText.textContent = "Analyzing..."
  } else {
    btnIcon.innerHTML = `<i class="ri-magic-line"></i>`
    btnText.textContent = "Analyze Resume"
  }
}

function humanSize(bytes) {
  const units = ["B", "KB", "MB", "GB"]
  let i = 0
  let n = bytes
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++ }
  return `${n.toFixed(n >= 10 || i === 0 ? 0 : 1)} ${units[i]}`
}

function onFileSelected(file) {
  const row = $("fileRow")
  const name = $("selectedFileName")
  const meta = $("selectedFileMeta")
  if (!row || !name || !meta) return

  if (!file) {
    row.style.display = "none"
    return
  }

  row.style.display = "flex"
  name.textContent = file.name
  meta.textContent = `${humanSize(file.size)} • ${file.type || "file"}`
}

async function uploadResume(file) {
  setBusy(true)
  toast("info", "Uploading and analyzing your resume...")

  const formData = new FormData()
  formData.append("resume", file)

  try {
    const res = await fetch("/upload_resume", {
      method: "POST",
      body: formData,
      credentials: "include"
    })

    if (res.status === 401) {
      toast("bad", "Session expired. Please login again.")
      setTimeout(goLogin, 600)
      return
    }

    if (res.redirected) {
      toast("good", "Analysis complete. Opening results…")
      window.location.href = res.url
      return
    }

    if (!res.ok) {
      const t = await res.text()
      console.log(t)
      toast("bad", "Analysis failed. Please try again.")
      setBusy(false)
      return
    }

    toast("good", "Done.")
  } catch (e) {
    toast("bad", "Network error. Please try again.")
  } finally {
    setBusy(false)
  }
}

async function loadCurrentUser() {
  const welcome = $("welcomeText")
  if (!welcome) return

  try {
    const res = await fetch("/current_user", { credentials: "include" })
    if (res.status === 401) return
    if (!res.ok) return
    const data = await res.json()
    const username = data.username || "User"
    welcome.textContent = `Welcome, ${username}`
  } catch (e) {}
}

async function loadDashboardUploads() {
  try {
    const res = await fetch("/my_uploads", { credentials: "include" })
    if (res.status === 401) {
      toast("bad", "Session expired. Please login again.")
      setTimeout(goLogin, 600)
      return
    }

    const html = await res.text()
    const doc = new DOMParser().parseFromString(html, "text/html")
    const rows = doc.querySelectorAll("tr.upload-row")

    const totalEl = $("totalUploads")
    if (totalEl) totalEl.textContent = rows.length

    const recent = $("recentResumes")
    if (recent) recent.innerHTML = ""

    if (!rows.length) {
      if (recent) recent.innerHTML = `<div class="empty">No uploads found yet. Upload a resume to see recent activity here.</div>`
      const best = $("bestScore")
      const avg = $("avgScore")
      if (best) best.textContent = "--"
      if (avg) avg.textContent = "--"
      return
    }

    // compute scores from ALL rows
    const scoresAll = []
    rows.forEach((row) => {
      const scoreText = row.children[2]?.textContent || ""
      const score = scoreText.match(/\d+/)?.[0]
      if (score) scoresAll.push(+score)
    })

    const best = $("bestScore")
    const avg = $("avgScore")
    if (scoresAll.length) {
      if (best) best.textContent = Math.max(...scoresAll)
      if (avg) avg.textContent = Math.round(scoresAll.reduce((a, b) => a + b, 0) / scoresAll.length)
    } else {
      if (best) best.textContent = "--"
      if (avg) avg.textContent = "--"
    }

    // show only 5 recent in UI
    const slice = Array.from(rows).slice(0, 5)
    slice.forEach((row) => {
      const name = row.children[0]?.textContent?.trim() || "Resume"
      const date = row.children[1]?.textContent?.trim() || ""
      const scoreText = row.children[2]?.textContent || ""
      const score = scoreText.match(/\d+/)?.[0]

      if (recent) {
        const el = document.createElement("div")
        el.className = "item"
        el.innerHTML = `
          <div class="left">
            <div class="title">${name}</div>
            <div class="date">${date}</div>
          </div>
          <div class="badge">${score ? score + " / 100" : "-- / 100"}</div>
        `
        recent.appendChild(el)
      }
    })
  } catch (e) {
    console.log(e)
  }
}

function wireUploadForm() {
  const form = $("uploadForm")
  const input = $("resumeInput")
  const drop = $("dropZone")

  if (input) {
    input.addEventListener("change", () => {
      droppedFile = null
      onFileSelected(input.files[0])
      if (input.files[0]) toast("info", "File selected. Click Analyze to start.")
    })
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault()
      const file = input?.files?.[0] || droppedFile
      if (!file) {
        toast("bad", "Please select a resume file.")
        return
      }
      await uploadResume(file)
    })
  }

  if (drop && input) {
    ;["dragenter", "dragover"].forEach(evt => {
      drop.addEventListener(evt, (e) => {
        e.preventDefault()
        e.stopPropagation()
        drop.classList.add("drag")
      })
    })
    ;["dragleave", "drop"].forEach(evt => {
      drop.addEventListener(evt, (e) => {
        e.preventDefault()
        e.stopPropagation()
        drop.classList.remove("drag")
      })
    })
    drop.addEventListener("drop", (e) => {
      const file = e.dataTransfer?.files?.[0]
      if (file) {
        droppedFile = file
        try { input.files = e.dataTransfer.files } catch (err) {}
        onFileSelected(file)
        toast("info", "File selected. Click Analyze to start.")
      }
    })
  }
}

wireUploadForm()
loadCurrentUser()
loadDashboardUploads()