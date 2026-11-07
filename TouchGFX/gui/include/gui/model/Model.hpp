#ifndef MODEL_HPP
#define MODEL_HPP

class ModelListener;

class Model {
public:
    Model();
    void bind(ModelListener* listener) { modelListener = listener; }
    void tick();
    void toggleBoostLed();
    bool isBoostActive() const { return boostActive; }

protected:
    ModelListener* modelListener;

private:
    int tickCounter;
    float currentTempC;
    int cpuLoadPercent;
    bool boostActive;
};

#endif // MODEL_HPP
