// Admin custom JavaScript for Pages app

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Auto-generate slug from title
        $('#id_title').on('blur', function() {
            var title = $(this).val();
            var slugField = $('#id_slug');
            
            if (title && !slugField.val()) {
                var slug = title.toLowerCase()
                    .replace(/[^\w\s-]/g, '') // Remove special characters
                    .replace(/\s+/g, '-') // Replace spaces with hyphens
                    .replace(/--+/g, '-'); // Replace multiple hyphens with single hyphen
                
                slugField.val(slug);
            }
        });
        
        // Show image preview
        $('.field-featured_image input[type="file"]').on('change', function(e) {
            var input = this;
            var preview = $('<div class="image-preview"></div>');
            
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                
                reader.onload = function(e) {
                    preview.html('<img src="' + e.target.result + '" class="img-fluid">');
                };
                
                reader.readAsDataURL(input.files[0]);
                
                // Remove existing preview
                $(input).siblings('.image-preview').remove();
                $(input).after(preview);
            }
        });
        
        // Character counters for textareas
        $('.field-excerpt textarea, .field-seo_description textarea').each(function() {
            var $textarea = $(this);
            var maxlength = $textarea.attr('maxlength');
            
            if (maxlength) {
                var counter = $('<small class="char-counter text-muted float-end">0/' + maxlength + '</small>');
                $textarea.after(counter);
                
                $textarea.on('keyup', function() {
                    var length = $textarea.val().length;
                    counter.text(length + '/' + maxlength);
                    
                    if (length > maxlength * 0.9) {
                        counter.addClass('text-danger').removeClass('text-muted');
                    } else {
                        counter.removeClass('text-danger').addClass('text-muted');
                    }
                }).trigger('keyup');
            }
        });
        
        // Toggle publish/expire dates based on status
        $('#id_status').on('change', function() {
            var status = $(this).val();
            var publishField = $('.field-publish_date');
            var expireField = $('.field-expire_date');
            
            if (status === 'published') {
                publishField.show();
                expireField.show();
            } else {
                publishField.hide();
                expireField.hide();
            }
        }).trigger('change');
        
        // Preview button in change form
        if ($('#page-form').length) {
            var previewUrl = $('a[href*="preview"]').attr('href');
            if (previewUrl) {
                var previewBtn = $('<a>')
                    .attr('href', previewUrl)
                    .attr('target', '_blank')
                    .addClass('button preview-btn')
                    .text('Preview')
                    .css({
                        'margin-left': '10px',
                        'color': 'white'
                    });
                
                $('.submit-row').append(previewBtn);
            }
        }
        
        // Bulk actions for comments
        $('.comment-actions select').on('change', function() {
            var action = $(this).val();
            var selected = $('.action-select:checked');
            
            if (action && selected.length > 0) {
                var ids = selected.map(function() {
                    return $(this).val();
                }).get();
                
                if (confirm('Are you sure?')) {
                    $.ajax({
                        url: window.location.href,
                        method: 'POST',
                        data: {
                            action: action,
                            ids: ids,
                            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                        },
                        success: function() {
                            location.reload();
                        }
                    });
                }
            }
        });
        
        // Real-time statistics
        if ($('.stats-box').length) {
            setInterval(function() {
                $.getJSON(window.location.href + 'stats/', function(data) {
                    $('.total-views').text(data.total_views);
                    $('.total-pages').text(data.total_pages);
                    $('.total-comments').text(data.total_comments);
                });
            }, 30000); // Update every 30 seconds
        }
        
        // Drag and drop for page ordering
        if ($('#result_list tbody').length) {
            $('#result_list tbody').sortable({
                axis: 'y',
                handle: '.drag-handle',
                update: function(event, ui) {
                    var order = [];
                    $('#result_list tbody tr').each(function(index) {
                        order.push({
                            id: $(this).find('.id').text(),
                            order: index
                        });
                    });
                    
                    $.ajax({
                        url: window.location.href + 'reorder/',
                        method: 'POST',
                        data: {
                            order: JSON.stringify(order),
                            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                        }
                    });
                }
            });
            
            // Add drag handle to rows
            $('#result_list tbody tr').each(function() {
                $(this).find('td:first').prepend('<span class="drag-handle" style="cursor: move; margin-right: 10px;">↕</span>');
            });
        }
    });
})(django.jQuery);