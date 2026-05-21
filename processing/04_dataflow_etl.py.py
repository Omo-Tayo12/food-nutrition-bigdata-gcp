import argparse
import json
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class CleanStreamingData(beam.DoFn):
    def process(self, element):
        try:
            # Load the incoming text message as JSON data
            record = json.loads(element.decode('utf-8'))
            # Basic cleaning: make sure text is clean and capitalized
            record['food_name'] = record.get('food_name', 'Unknown').strip().title()
            record['food_group'] = record.get('food_group', 'Uncategorized').strip()
            yield record
        except Exception as e:
            logging.error(f"Error processing streaming line: {e}")

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_topic', default='projects/your-gcp-project-id/topics/food-nutrition-updates')
    parser.add_argument('--output_table', default='your-gcp-project-id:nutrition.streaming_nutrition_logs')
    args, beam_args = parser.parse_known_args()

    options = PipelineOptions(beam_args)
    with beam.Pipeline(options=options) as p:
        (
            p 
            | "Read from PubSub" >> beam.io.ReadFromPubSub(topic=args.input_topic)
            | "Clean Streaming Elements" >> beam.ParDo(CleanStreamingData())
            | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                args.output_table,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()