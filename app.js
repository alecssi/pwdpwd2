'use strict';
const root = document.documentElement;
const toggle = document.getElementById('sidebar-toggle');
const sidebar = document.getElementById('sidebar');
const mobile = window.matchMedia('(max-width:850px)');
function syncSidebar() {
  const open = mobile.matches ? root.classList.contains('sidebar-mobile-open') : !root.classList.contains('sidebar-collapsed');
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Hide Sidebar' : 'Show Sidebar');
  toggle.title = open ? 'Hide Sidebar' : 'Show Sidebar';
  toggle.querySelector('.toggle-caption').textContent = open ? 'Hide Menu' : 'Show Menu';
  sidebar.inert = !open;
}
function closeMobile() { root.classList.remove('sidebar-mobile-open'); syncSidebar(); }
if (toggle && sidebar) {
  syncSidebar();
  toggle.addEventListener('click', () => {
    if (mobile.matches) root.classList.toggle('sidebar-mobile-open');
    else {
      root.classList.toggle('sidebar-collapsed');
      try { localStorage.setItem('qn.v4.sidebar', root.classList.contains('sidebar-collapsed') ? 'closed' : 'open'); } catch (e) {}
    }
    syncSidebar();
  });
  document.getElementById('sidebar-overlay').addEventListener('click', closeMobile);
  if (mobile.addEventListener) mobile.addEventListener('change', closeMobile); else mobile.addListener(closeMobile);
  document.addEventListener('keydown', e => { if(e.key==='Escape' && root.classList.contains('sidebar-mobile-open')) {closeMobile(); toggle.focus();} });
}
// Patient name selector. Keep the unique ID as the actual submitted value.
document.querySelectorAll('.patient-filter').forEach(input => {
  const select = input.closest('form').querySelector('.patient-select');
  if (!select) return;
  const options = Array.from(select.options).map(o => o.cloneNode(true));
  input.addEventListener('input', () => {
    const selected = select.value;
    const words = input.value.trim().toLowerCase().replace(/,/g,' ').split(/\s+/).filter(Boolean);
    const matching = options.filter(o => !o.value || words.every(w=>o.textContent.toLowerCase().includes(w)));
    select.replaceChildren(...matching.map(o => o.cloneNode(true)));
    select.value = matching.some(o=>o.value===selected) ? selected : '';
    if (select.options.length===2) select.selectedIndex=1;
    if (select.options.length===1) select.options[0].textContent='No Patients Found';
  });
});
// Directory display preference.
const views = Array.from(document.querySelectorAll('[data-view]'));
function setView(view) {
  if (!['cards','table'].includes(view)) view='cards';
  document.getElementById('cards-view').hidden = view!=='cards';
  document.getElementById('table-view').hidden = view!=='table';
  views.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
  try {localStorage.setItem('qn.v4.recordsView',view);} catch(e) {}
}
if (views.length) { let pref='cards';try{pref=localStorage.getItem('qn.v4.recordsView')||'cards';}catch(e){}setView(pref);views.forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view))); }
// Accessible profile tabs, with arrow-key navigation.
document.querySelectorAll('[data-tabs]').forEach(group => {
  const tabs = Array.from(group.querySelectorAll('[role=tab]'));
  function activate(tab,focus=false) {tabs.forEach(t=>{const on=t===tab;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!on;});if(focus)tab.focus();}
  activate(tabs[0]);
  tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>activate(tab));tab.addEventListener('keydown',e=>{let target;if(e.key==='ArrowRight')target=tabs[(i+1)%tabs.length];if(e.key==='ArrowLeft')target=tabs[(i+tabs.length-1)%tabs.length];if(e.key==='Home')target=tabs[0];if(e.key==='End')target=tabs[tabs.length-1];if(target){e.preventDefault();activate(target,true);}});});
});
document.querySelectorAll('form[data-confirm]').forEach(form=>form.addEventListener('submit',e=>{if(!confirm(form.dataset.confirm))e.preventDefault();}));
