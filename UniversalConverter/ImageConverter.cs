using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Processing;
using SixLabors.ImageSharp.Formats.Gif;
using SixLabors.ImageSharp.Formats.Webp;
using SixLabors.ImageSharp.Processing.Processors.Quantization;

namespace UniversalConverter
{
    public class ConversionOptions
    {
        public int WebpQuality { get; set; } = 75;
        public ushort GifRepeatCount { get; set; } = 0; // 0 for infinite loop
    }

    public class ImageConverter
    {
        public void ConvertWebPToGif(string inputPath, string outputPath, ConversionOptions options)
        {
            using (Image image = Image.Load(inputPath))
            {
                var quantizer = new WuQuantizer(new QuantizerOptions
                {
                    MaxColors = 255,
                    Dither = new FloydSteinbergDither()
                });

                var encoder = new GifEncoder
                {
                    Quantizer = quantizer,
                };

                image.Metadata.GetGifMetadata().RepeatCount = options.GifRepeatCount;

                image.SaveAsGif(outputPath, encoder);
            }
        }

        public void ConvertGifToWebP(string inputPath, string outputPath, ConversionOptions options)
        {
            using (Image image = Image.Load(inputPath))
            {
                var encoder = new WebpEncoder
                {
                    Quality = options.WebpQuality
                };

                image.SaveAsWebp(outputPath, encoder);
            }
        }
    }
}