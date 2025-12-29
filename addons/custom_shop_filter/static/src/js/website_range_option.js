import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteRangeOption = publicWidget.Widget.extend({
    selector: '.o_wsale_products_page',
    events: {
        'change input.custom-range-filter[type="range"]': '_onRangeChange',
    },

    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this._initializeRangesFromUrl();
        this._updateAllRangeDisplays();
        return this;
    },

    /**
     * Initialize range values from URL parameters
     */
    _initializeRangesFromUrl: function () {
        const urlParams = new URLSearchParams(window.location.search);
        this.$el.find('input.custom-range-filter[type="range"]').each((index, element) => {
            const attributeId = element.dataset.attributeId;
            if (!attributeId) return;

            const minParam = `current_min_${attributeId}`;
            const maxParam = `current_max_${attributeId}`;
            const urlMin = urlParams.get(minParam);
            const urlMax = urlParams.get(maxParam);

            // We check if there are parameters
            if (urlMin !== null && urlMax !== null) {
                try {
                    const minValue = parseInt(urlMin) || parseInt(element.min);
                    const maxValue = parseInt(urlMax) || parseInt(element.max);
                    if (!isNaN(minValue) && !isNaN(maxValue)) {
                        element.setAttribute('cmin', minValue);
                        element.setAttribute('cmax', maxValue);
                        element.setAttribute('value', [minValue, maxValue]);
                        this._updateRangeDisplay(element);
                    }
                } catch (error) {
                    console.debug('Error setting range values:', error);
                }
            }
        });
    },

    /**
     * Handle range change
     */
    _onRangeChange: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const element = ev.currentTarget;
        const attributeId = element.dataset.attributeId;
        if (!attributeId) return;

        const values = element.value.split(',').map(val => parseInt(val.trim()));

        // We check if we have moved the maximum or the minimum
        let minValue, maxValue
        if (values.length !== 2){
            maxValue = values[0]
            minValue = element.getAttribute('cmin')
        }
        else {
            minValue = values[0]
            maxValue = values[1]
        }

        // Check that the minimum is less than the maximum
        if (minValue > maxValue) {
            [minValue, maxValue] = [maxValue, minValue];
        }

        // We save the current range
        element.setAttribute('cmin', minValue)
        element.setAttribute('cmax', maxValue)

        this._updateRangeDisplay(element);
        this._updateUrl(attributeId, minValue, maxValue);
    },

    /**
     * Update URL parameters
     */
    _updateUrl: function (attributeId, minValue, maxValue) {
        console.log('Función updateUrl')
        console.log('minValue: ', minValue)
        console.log('maxValue: ', maxValue)
        const url = new URL(window.location);

        // Actualizar parámetros
        url.searchParams.set(`current_min_${attributeId}`, minValue);
        url.searchParams.set(`current_max_${attributeId}`, maxValue);

        // Remover parámetro de página para volver a la primera
        url.searchParams.delete('page');

        // Usar replaceState para actualizar la URL sin recargar
        window.history.replaceState({}, '', url.toString());

        // Enviar el formulario de búsqueda para aplicar el filtro
        this._submitSearchForm();
    },

    /**
     * Submit search form
     */
    _submitSearchForm: function () {
        const $form = this.$el.find('form.js_products_search');

        if ($form.length) {
            // Add a small delay to prevent multiple quick submits
            if (this._submitTimeout) {
                clearTimeout(this._submitTimeout);
            }

            this._submitTimeout = setTimeout(() => {
                // Submit the form to apply the filters
                $form.submit();
            }, 300);
        } else {
            // Reload the page with the new parameters
            window.location.href = window.location.href;
        }
    },

    /**
     * Update display for a single range
     */
    _updateRangeDisplay: function (range) {
        // We apply the range filters to the sale filter container, which is the one we are using.
        let $container = $(range).closest('.range-filter-container');
        if (!$container.length) {
            $container = $(range).closest('.accordion-item').find('.accordion-collapse');
        }
        if (!$container.length) {
            $container = $(range).parent();
        }
    },

    /**
     * Initialize all range displays
     * Necessary when there is more than one attribute of type range
     */
    _updateAllRangeDisplays: function () {
        console.log('Función updateAllRangeDisplays')
        this.$el.find('input.custom-range-filter[type="range"]').each((index, element) => {
            this._updateRangeDisplay(element);
        });
    }
});