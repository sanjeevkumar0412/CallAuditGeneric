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
                url: 'http://flm-vm-cogaidev:4091/get_data_from_sentiment_table',
                type: 'GET',
                dataType: 'json',
                data: {
                    clientid: clientId,
                    audio_file: audioFileName
                },
                success: function(data) {
                    // Hide loader
					console.log(2222222222,data);
                    $('.loader').hide();
                    $('.form-group').hide();
                    $('#submitButton').hide();
                    $('#sentimentTable').show();
                    $('#backsentiment').show();
                    // Remove ClientId and Id keys from the response

                    delete data.ClientId;
                    delete data.Created;
                    delete data.Modified;
                    delete data.SentimentStatus;
                    delete data.SentimentScore;
                    delete data.Id;
                    // Populate table body with data
                    var sentimentData = data;
                    var tableBody = $('#sentimentData');
                    // Append AudioFileName first

				row = $('<tr></tr>');
						row.append($('<td></td>').text('AudioFileName'));
						row.append($('<td class="td_break_all"></td>').text(sentimentData.AudioFileName));
						//$('.audio_cls').show();
						tableBody.append(row);
				row = $('<tr></tr>');
                    row.append($('<td></td>').text('ActionItemsOwners'));
                    row.append($('<td class="td_break_all"></td>').text(sentimentData.ActionItemsOwners));
                    tableBody.append(row);
                row = $('<tr></tr>');
                row.append($('<td></td>').text('Sentiment'));
                row.append($('<td class="td_break_all"></td>').text(sentimentData.Sentiment));
                tableBody.append(row);

                row = $('<tr></tr>');
                    row.append($('<td></td>').text('FoulLanguage'));
                    row.append($('<td class="td_break_all"></td>').text(sentimentData.FoulLanguage));
                    tableBody.append(row);

                row = $('<tr></tr>');
                    row.append($('<td></td>').text('SummaryReport'));
                    row.append($('<td class="td_break_all"></td>').text(sentimentData.SummaryReport));
                    tableBody.append(row);

                row = $('<tr></tr>');
                    row.append($('<td></td>').text('Topics'));
                    row.append($('<td class="td_break_all"></td>').text(sentimentData.Topics));
                    tableBody.append(row);

                     row = $('<tr></tr>');
                    row.append($('<td></td>').text('Reminder'));
                    row.append($('<td class="td_break_all"></td>').text(sentimentData.Reminder));
                    tableBody.append(row);
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
                    $('.loader').hide();
                    $('#sentimentTable').hide();
                    console.error('Error fetching sentiment data:', audioFileName);
                    // Hide loader
                    alert("Record not available", audioFileName);
                }
            });
        });
    });