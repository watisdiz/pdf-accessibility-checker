const form = document.querySelector('#upload-form');
const fileInput = document.querySelector('#pdf-file');
const dropZone = document.querySelector('#drop-zone');
const selectedFile = document.querySelector('#selected-file');
const submitButton = document.querySelector('#submit-button');
const statusRegion = document.querySelector('#status');
const resultSection = document.querySelector('#result');
const downloadButton = document.querySelector('#download-json');
let latestResult = null;

function setFile(file) {
  if (!file) {
    selectedFile.textContent = 'Ei valittua tiedostoa.';
    submitButton.disabled = true;
    return;
  }
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  selectedFile.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} Mt)`;
  submitButton.disabled = false;
}

fileInput.addEventListener('change', () => setFile(fileInput.files[0]));

['dragenter', 'dragover'].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add('is-dragging');
  });
});

['dragleave', 'drop'].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove('is-dragging');
  });
});

dropZone.addEventListener('drop', (event) => setFile(event.dataTransfer.files[0]));

function renderIssues(issues) {
  const container = document.querySelector('#issues');
  container.replaceChildren();
  if (!issues.length) {
    const message = document.createElement('p');
    message.textContent = 'Epäonnistuneita koneellisia sääntöjä ei löytynyt.';
    container.append(message);
    return;
  }

  issues.forEach((issue) => {
    const details = document.createElement('details');
    details.className = 'issue';
    const summary = document.createElement('summary');
    summary.textContent = `${issue.specification}, kohta ${issue.clause} · ${issue.occurrences} esiintymää`;
    const body = document.createElement('div');
    body.className = 'issue__body';

    const description = document.createElement('p');
    description.textContent = issue.description || 'Ei kuvausta.';
    body.append(description);

    const meta = document.createElement('p');
    meta.className = 'issue__meta';
    meta.textContent = `Testi ${issue.test_number || '–'} · Kohde ${issue.object || '–'}`;
    body.append(meta);

    if (issue.contexts.length) {
      const heading = document.createElement('strong');
      heading.textContent = 'Tekniset kontekstit';
      body.append(heading);
      const list = document.createElement('ul');
      issue.contexts.forEach((context) => {
        const item = document.createElement('li');
        const code = document.createElement('code');
        code.textContent = context;
        item.append(code);
        list.append(item);
      });
      body.append(list);
    }

    details.append(summary, body);
    container.append(details);
  });
}

function renderResult(result) {
  latestResult = result;
  const compliant = result.status === 'compliant';
  resultSection.hidden = false;
  resultSection.classList.toggle('is-compliant', compliant);
  resultSection.classList.toggle('is-non-compliant', !compliant);
  document.querySelector('#result-kicker').textContent = result.profile;
  document.querySelector('#result-summary').textContent = compliant
    ? 'PDF läpäisi veraPDF:n koneellisesti tarkistettavat PDF/UA-1-säännöt.'
    : 'PDF ei läpäissyt kaikkia veraPDF:n koneellisesti tarkistettavia PDF/UA-1-sääntöjä.';
  document.querySelector('#failed-rules').textContent = result.summary.failed_rules;
  document.querySelector('#failed-checks').textContent = result.summary.failed_checks;
  document.querySelector('#passed-rules').textContent = result.summary.passed_rules;
  document.querySelector('#duration').textContent = `${(result.duration_ms / 1000).toFixed(2)} s`;
  renderIssues(result.issues);
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  submitButton.disabled = true;
  statusRegion.classList.remove('error');
  statusRegion.textContent = 'PDF:ää ladataan ja tarkistetaan…';
  resultSection.hidden = true;

  const data = new FormData();
  data.append('file', file);

  try {
    const response = await fetch('/api/validate', { method: 'POST', body: data });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || 'Tarkistus epäonnistui.');
    statusRegion.textContent = 'Tarkistus valmis.';
    renderResult(payload);
  } catch (error) {
    statusRegion.classList.add('error');
    statusRegion.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
});

downloadButton.addEventListener('click', () => {
  if (!latestResult) return;
  const blob = new Blob([JSON.stringify(latestResult, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'pdf-ua-1-report.json';
  link.click();
  URL.revokeObjectURL(url);
});
