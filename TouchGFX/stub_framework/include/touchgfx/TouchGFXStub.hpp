#ifndef TOUCHGFX_STUB_HEADERS_HPP
#define TOUCHGFX_STUB_HEADERS_HPP
#include <stdint.h>

namespace touchgfx {

typedef uint32_t colortype;

struct Color {
    static colortype getColorFromRGB(uint8_t r, uint8_t g, uint8_t b) {
        return (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) | b;
    }
};

struct Bitmap {
    uint16_t id;
    explicit Bitmap(uint16_t bmpId = 0) : id(bmpId) {}
};

struct TypedText {
    uint16_t id;
    explicit TypedText(uint16_t textId = 0) : id(textId) {}
};

struct Unicode {
    typedef uint16_t UnicodeChar;
    static void snprintfFloat(UnicodeChar* dst, uint16_t size, const char* fmt, float val) {
        if (dst && size > 0) dst[0] = static_cast<UnicodeChar>(val);
    }
};

class Drawable {
public:
    virtual ~Drawable() {}
    void setPosition(int16_t x, int16_t y, int16_t w, int16_t h) {}
    void setXY(int16_t x, int16_t y) {}
    void invalidate() {}
};

class AbstractButton : public Drawable {};

class GenericCallbackBase {
public:
    virtual ~GenericCallbackBase() {}
};

template <class T, typename P1>
class Callback : public GenericCallbackBase {
public:
    Callback(T* pinst, void (T::*pmem)(P1)) : inst(pinst), mem(pmem) {}
private:
    T* inst;
    void (T::*mem)(P1);
};

class Box : public Drawable {
public:
    void setColor(colortype c) {}
};

class Image : public Drawable {
public:
    void setBitmap(const Bitmap& bmp) {}
};

class TextArea : public Drawable {
public:
    void setColor(colortype c) {}
    void setTypedText(const TypedText& t) {}
};

class TextAreaWithOneWildcard : public TextArea {
public:
    void setWildcard(const Unicode::UnicodeChar* buf) {}
};

class ButtonWithLabel : public AbstractButton {
public:
    void setBitmaps(const Bitmap& rel, const Bitmap& prs) {}
    void setLabelText(const TypedText& t) {}
    void setLabelColor(colortype c) {}
    void setLabelColorPressed(colortype c) {}
    void setAction(GenericCallbackBase& cb) {}
};

class BoxProgress : public Drawable {
public:
    void setProgressIndicatorPosition(int16_t x, int16_t y, int16_t w, int16_t h) {}
    void setRange(int minV, int maxV, uint16_t steps = 0, uint16_t minStep = 0) {}
    void setColor(colortype c) {}
    void setBackground(const Bitmap& bmp) {}
    void setValue(int v) {}
};

class Application {
public:
    static Application* getInstance() {
        static Application instance;
        return &instance;
    }
    virtual ~Application() {}
};

class ViewBase {
public:
    virtual ~ViewBase() {}
    virtual void setupScreen() {}
    virtual void tearDownScreen() {}
protected:
    void add(Drawable& d) {}
};

} // namespace touchgfx

#endif // TOUCHGFX_STUB_HEADERS_HPP
