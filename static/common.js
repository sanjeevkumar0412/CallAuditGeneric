$(document).ready(function() {
        $('#submitButton').click(function() {
            var clientId = $('#clientId').val();
            var audioFileName = $('#audioFileName').val();
            // Show loader
            if (clientId.trim() === '' || audioFileName.trim() === '') {
                alert('Please fill in all fields');
                return; // Exit function if fields are empty
            }
            $('#sentimentTable').hide();
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
                    $('#audio-filename').text(data.AudioFileName);
                    $('#sentiment').text(data.Sentiment);
                    $('#foul_lang').text(data.FoulLanguage);
                    $('#summary_report').text(data.SummaryReport);
                    $('#reminder').text(data.Reminder);
					console.log(2222222222,data);
                    $('.loader').hide();
                    $('.form-group').hide();
                    $('#submitButton').hide();
                    $('#sentimentTable').show();
                    $('#backsentiment').show();
                    // Populate table body with data
                    $('#sentimentTable').show();
                    var sentimentData = data;
                    // var tableBody = $('#sentimentData');
                    var action_owner=data.ActionItemsOwners;
                    var jsonStringWithDoubleQuotes = action_owner.replace(/'/g, '"');
                    var action_owner_data=JSON.parse(jsonStringWithDoubleQuotes);
                    var summary_topics=data.Topics;
                    var topics_jsonStringWithDoubleQuotes = summary_topics.replace(/'/g, '"');
                    var summary_topics_data=JSON.parse(topics_jsonStringWithDoubleQuotes);
                    var html = '';
                       $.each(action_owner_data, function(key, value) {
                           // console.log("Key",key);
                           // console.log("Date value", value.Date);

                           html += '<tr>';
                           html += '<td>' + (value.ActionItem) + '</td>';
                           html += '<td>' + value.ActionOwner + '</td>';
                           html += '<td>' + value.ActionDate + '</td>';
                       });
                        $('#action_item_owner tbody').html(html);

                        var html_topics = '';
                    $.each(summary_topics_data, function(index, item) {
                            // console.log("Key",index);
                            // console.log("value",item);
                            html_topics += '<tr>';
                            html_topics += '<td>' + item.Topic + '</td>';
                            html_topics += '<td>' + item.Description + '</td>';
                            html_topics += '<td>' + item.Sentiment + '</td>';
                            html_topics += '</tr>';
                        });

                       $('#summary_topics tbody').html(html_topics);
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
        $('#sentimentTable').hide();
    });