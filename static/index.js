function ViewModel() {
    var self = this;
    self.url = ko.observable();
    self.imgUrls = ko.observableArray([]);
};

function fetchImages() {
    ajax.fetchImages(viewModel.url());
};

ajax = {
    fetchImages: function () {
        return $.ajax({
            type: "PUT",
            data: ko.toJSON({'base_url': viewModel.url()}),
            contentType: 'application/json',
            url: '/fetch-images',
            success: function (response) {
                viewModel.imgUrls(response);
            },
            error: function (response) {
            }
        });
    },
};

$(document).ready(function() {
    $(document).on('keydown', '#url', function(event) {
        if(event.keyCode === 13) {
            $('#url').blur().focus();
            ajax.fetchImages();
            event.preventDefault();
        }
    });
});

var viewModel = new ViewModel();
ko.applyBindings(viewModel, document.getElementById('container'));
