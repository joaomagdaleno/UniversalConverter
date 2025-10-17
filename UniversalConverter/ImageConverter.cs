using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Processing;
using SixLabors.ImageSharp.Formats.Gif;
using SixLabors.ImageSharp.Formats.Webp;
using SixLabors.ImageSharp.Formats.Png;
using SixLabors.ImageSharp.Formats.Jpeg;
using SixLabors.ImageSharp.Processing.Processors.Quantization;
using System.IO;

namespace UniversalConverter
{
    public class ConversionOptions
    {
        public int WebpQuality { get; set; } = 75;
        public ushort GifRepeatCount { get; set; } = 0; // 0 for infinite loop
        public int JpgQuality { get; set; } = 75;
        public PngCompressionLevel PngCompression { get; set; } = PngCompressionLevel.Default;
    }

    public class ImageConverter
    {
        public void ConvertImage(string inputPath, string outputPath, ConversionOptions options)
        {
            using (Image image = Image.Load(inputPath))
            {
                string outputExtension = Path.GetExtension(outputPath).ToLower();

                switch (outputExtension)
                {
                    case ".gif":
                        var gifQuantizer = new WuQuantizer(new QuantizerOptions
                        {
                            MaxColors = 255,
                            Dither = new FloydSteinbergDither()
                        });
                        var gifEncoder = new GifEncoder
                        {
                            Quantizer = gifQuantizer,
                        };
                        image.Metadata.GetGifMetadata().RepeatCount = options.GifRepeatCount;
                        image.SaveAsGif(outputPath, gifEncoder);
                        break;

                    case ".webp":
                        var webpEncoder = new WebpEncoder { Quality = options.WebpQuality };
                        image.SaveAsWebp(outputPath, webpEncoder);
                        break;

                    case ".jpg":
                    case ".jpeg":
                        var jpegEncoder = new JpegEncoder { Quality = options.JpgQuality };
                        image.SaveAsJpeg(outputPath, jpegEncoder);
                        break;

                    case ".png":
                        var pngEncoder = new PngEncoder { CompressionLevel = options.PngCompression };
                        image.SaveAsPng(outputPath, pngEncoder);
                        break;

                    default:
                        throw new NotSupportedException($"Formato de saída '{outputExtension}' não é suportado.");
                }
            }
        }
    }
}