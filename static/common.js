$(document).ready(function() {
        $('#submitButton').click(function() {
            var clientId = $('#clientId').val();
            var audioFileName = $('#audioFileName').val();
            // Show loader
            if (clientId.trim() === '' || audioFileName.trim() === '') {
                alert('Please fill in all fields');
                return; // Exit function if fields are empty
            }
            $('.loader').show();
            // $('#sentimentTable').show();
            // Make AJAX call to retrieve sentiment data
            $.ajax({
                url: '/get_data_from_sentiment_table',
                type: 'GET',
                dataType: 'json',
                data: {
                    clientid: clientId,
                    audio_file: audioFileName
                },
                success: function(data) {
                    // Hide loader
                    $('.loader').hide();
                    $('.form-group').hide();
                    $('#submitButton').hide();
                    $('#sentimentTable').show();
                    $('#backsentiment').show();
                    // Remove ClientId and Id keys from the response
                    delete data.ClientId;
                    delete data.Id;
                    // Populate table body with data
                    var sentimentData = data;
					console.log(">>>>",Object.keys(sentimentData).length);
                    var tableBody = $('#sentimentData');
                    // Append AudioFileName first
                    var row = $('<tr class="audio_cls"></tr>');
                    row.append($('<td></td>').text('AudioFileName'));
                    row.append($('<td></td>').text(sentimentData.AudioFileName));
					$('.audio_cls').show();
                    tableBody.empty().append(row);
                    // Append ActionItems next
                    row = $('<tr class="audio_cls"></tr>');
                    row.append($('<td></td>').text('ActionItems'));
                    row.append($('<td></td>').text(sentimentData.ActionItems));
                    tableBody.append(row);
                    // Append other data in the original order
					console.log(sentimentData);
                    $.each(sentimentData, function(key, value) {
                        if (key !== 'AudioFileName' && key !== 'ActionItems') {
                            var row = $('<tr></tr>');
                            row.append($('<td></td>').text(key));
                            row.append($('<td></td>').text(value));
                            tableBody.append(row);
                        }
                    });
					if(sentimentData.ActionItems === undefined) {
					console.log('If Condition');
							$('.audio_cls').hide();
							//$('.audio_cls1').hide();
							//$('.audio_cls:not(:eq(0), :eq(1))').hide();
						}
				else {
						$('.audio_cls:not(:eq(0), :eq(1))').show();
				}
                },
                error: function(xhr, status, error) {
					$('#sentimentTable').find('thead').hide();
                    $('.loader').hide();
                    $('#sentimentTable').hide();
                    console.error('Error fetching sentiment data:', audioFileName);
                    // Hide loader
                    alert("Record not available", audioFileName);
                }
            });
        });
    });