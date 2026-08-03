(function () {
    var instanceCount = 0;

    function enhance(select) {
        instanceCount += 1;
        var listboxId = 'multiselect-listbox-' + instanceCount;

        var wrapper = document.createElement('div');
        wrapper.className = 'multiselect';

        var chips = document.createElement('div');
        chips.className = 'multiselect-chips';

        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'multiselect-input';
        input.placeholder = 'Type to search…';
        input.autocomplete = 'off';
        input.setAttribute('role', 'combobox');
        input.setAttribute('aria-expanded', 'false');
        input.setAttribute('aria-autocomplete', 'list');
        input.setAttribute('aria-controls', listboxId);
        if (select.id) {
            input.id = select.id;
            select.removeAttribute('id');
        }

        var dropdown = document.createElement('ul');
        dropdown.id = listboxId;
        dropdown.className = 'multiselect-dropdown';
        dropdown.setAttribute('role', 'listbox');
        dropdown.hidden = true;

        var inputWrap = document.createElement('div');
        inputWrap.className = 'multiselect-input-wrap';
        inputWrap.appendChild(input);
        inputWrap.appendChild(dropdown);

        wrapper.appendChild(chips);
        wrapper.appendChild(inputWrap);

        select.classList.add('multiselect-native');
        select.insertAdjacentElement('afterend', wrapper);

        var activeIndex = -1;
        var currentMatches = [];

        function optionList() {
            return Array.prototype.slice.call(select.options);
        }

        function renderChips() {
            chips.innerHTML = '';
            optionList().filter(function (o) { return o.selected; }).forEach(function (o) {
                var chip = document.createElement('span');
                chip.className = 'tag multiselect-chip';
                chip.textContent = o.textContent;

                var remove = document.createElement('button');
                remove.type = 'button';
                remove.className = 'multiselect-chip-remove';
                remove.setAttribute('aria-label', 'Remove ' + o.textContent);
                remove.textContent = '×';
                remove.addEventListener('click', function () {
                    o.selected = false;
                    renderChips();
                    renderDropdown();
                });

                chip.appendChild(remove);
                chips.appendChild(chip);
            });
        }

        function setActive(index) {
            var items = dropdown.querySelectorAll('.multiselect-option');
            items.forEach(function (item) { item.classList.remove('is-active'); });
            activeIndex = index;
            if (index >= 0 && index < items.length) {
                items[index].classList.add('is-active');
                items[index].scrollIntoView({ block: 'nearest' });
                input.setAttribute('aria-activedescendant', items[index].id);
            } else {
                input.removeAttribute('aria-activedescendant');
            }
        }

        function selectOption(o) {
            o.selected = true;
            input.value = '';
            renderChips();
            renderDropdown();
            input.focus();
        }

        function renderDropdown() {
            var query = input.value.trim().toLowerCase();
            dropdown.innerHTML = '';
            activeIndex = -1;
            input.removeAttribute('aria-activedescendant');
            currentMatches = optionList().filter(function (o) {
                return !o.selected && (!query || o.textContent.toLowerCase().indexOf(query) !== -1);
            }).slice(0, 50);

            if (!currentMatches.length) {
                dropdown.hidden = true;
                input.setAttribute('aria-expanded', 'false');
                return;
            }

            currentMatches.forEach(function (o, index) {
                var item = document.createElement('li');
                item.id = listboxId + '-option-' + index;
                item.className = 'multiselect-option';
                item.setAttribute('role', 'option');
                item.textContent = o.textContent;
                item.addEventListener('mousedown', function (e) {
                    e.preventDefault();
                    selectOption(o);
                });
                dropdown.appendChild(item);
            });
            dropdown.hidden = false;
            input.setAttribute('aria-expanded', 'true');
        }

        input.addEventListener('input', renderDropdown);
        input.addEventListener('focus', renderDropdown);
        input.addEventListener('blur', function () {
            window.setTimeout(function () {
                dropdown.hidden = true;
                input.setAttribute('aria-expanded', 'false');
            }, 100);
        });
        input.addEventListener('keydown', function (e) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (dropdown.hidden) { renderDropdown(); }
                setActive(Math.min(activeIndex + 1, currentMatches.length - 1));
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setActive(Math.max(activeIndex - 1, 0));
            } else if (e.key === 'Enter') {
                if (!dropdown.hidden && activeIndex >= 0 && currentMatches[activeIndex]) {
                    e.preventDefault();
                    selectOption(currentMatches[activeIndex]);
                }
            } else if (e.key === 'Escape') {
                dropdown.hidden = true;
                input.setAttribute('aria-expanded', 'false');
            } else if (e.key === 'Backspace' && !input.value) {
                var selected = optionList().filter(function (o) { return o.selected; });
                var last = selected[selected.length - 1];
                if (last) {
                    last.selected = false;
                    renderChips();
                    renderDropdown();
                }
            }
        });

        renderChips();
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('select.js-multiselect').forEach(enhance);
    });
})();
