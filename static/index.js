function ViewModel() {
    var self = this;
    self.url = ko.observable();
    self.imgUrls = ko.observableArray([]);
    self.isBusy = ko.observable(false);

    self.busyIndicationStatus = ko.computed(function() {
        if(self.isBusy()) {
            $('#url').attr('disabled', 'disabled');
            $('#fetch-btn').attr('disabled', 'disabled');
        } else {
            $('#url').removeAttr('disabled');
            $('#fetch-btn').removeAttr('disabled');
        }
    });
};

function fetchImages() {
    ajax.fetchImages(viewModel.url());
};

ajax = {
    fetchImages: function () {
        viewModel.isBusy(true);

        return $.ajax({
            type: 'PUT',
            data: ko.toJSON({'base_url': viewModel.url()}),
            contentType: 'application/json',
            url: '/fetch-images',
            success: function (response) {
                viewModel.imgUrls(response);
                viewModel.isBusy(false);
            },
            error: function (response) {
                alert('Something went wrong, please try again');
                viewModel.isBusy(false);
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
