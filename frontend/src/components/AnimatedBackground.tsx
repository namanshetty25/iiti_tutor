import React from 'react';

const AnimatedBackground: React.FC = () => {
    return (
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
            {/* Primary gradient orb */}
            <div
                className="absolute w-[600px] h-[600px] rounded-full opacity-30 dark:opacity-20 animate-float blur-3xl"
                style={{
                    background: 'radial-gradient(circle, rgba(34, 211, 238, 0.4) 0%, transparent 70%)',
                    top: '-10%',
                    right: '-10%',
                }}
            />

            {/* Secondary gradient orb */}
            <div
                className="absolute w-[500px] h-[500px] rounded-full opacity-25 dark:opacity-15 animate-float-delayed blur-3xl"
                style={{
                    background: 'radial-gradient(circle, rgba(168, 85, 247, 0.4) 0%, transparent 70%)',
                    bottom: '-5%',
                    left: '-5%',
                }}
            />

            {/* Accent orb */}
            <div
                className="absolute w-[300px] h-[300px] rounded-full opacity-20 dark:opacity-10 animate-float blur-2xl"
                style={{
                    background: 'radial-gradient(circle, rgba(236, 72, 153, 0.3) 0%, transparent 70%)',
                    top: '40%',
                    left: '30%',
                    animationDelay: '2s',
                }}
            />

            {/* Light theme mesh gradient overlay */}
            <div className="absolute inset-0 dark:hidden opacity-50"
                style={{
                    background: 'radial-gradient(ellipse at top right, rgba(99, 179, 237, 0.15) 0%, transparent 50%), radial-gradient(ellipse at bottom left, rgba(167, 139, 250, 0.1) 0%, transparent 50%)',
                }}
            />

            {/* Dark theme subtle grid pattern */}
            <div
                className="absolute inset-0 hidden dark:block opacity-[0.03]"
                style={{
                    backgroundImage: `linear-gradient(rgba(34, 211, 238, 0.5) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(34, 211, 238, 0.5) 1px, transparent 1px)`,
                    backgroundSize: '50px 50px',
                }}
            />
        </div>
    );
};

export default AnimatedBackground;
