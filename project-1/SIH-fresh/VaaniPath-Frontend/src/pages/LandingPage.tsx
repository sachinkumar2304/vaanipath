import { Link } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { PremiumBackground } from '@/components/ui/PremiumBackground';
import {
  GraduationCap,
  Languages,
  Video,
  Users,
  Globe,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  PlayCircle
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

const LandingPage = () => {
  const { t } = useTranslation();
  const features = [
    {
      icon: Languages,
      title: t('landing.multilingualSupport'),
      description: t('landing.multilingualDesc'),
      color: 'text-blue-500',
      bg: 'bg-blue-500/10'
    },
    {
      icon: Video,
      title: t('landing.videoLectures'),
      description: t('landing.videoLecturesDesc'),
      color: 'text-purple-500',
      bg: 'bg-purple-500/10'
    },
    {
      icon: Users,
      title: t('landing.expertTeachers'),
      description: t('landing.expertTeachersDesc'),
      color: 'text-pink-500',
      bg: 'bg-pink-500/10'
    },
    {
      icon: Globe,
      title: t('landing.regionalContent'),
      description: t('landing.regionalContentDesc'),
      color: 'text-orange-500',
      bg: 'bg-orange-500/10'
    },
  ];

  const benefits = [
    t('landing.aiTranslation'),
    t('landing.selfPaced'),
    t('landing.progressTracking'),
    t('landing.interactiveLearning'),
    t('landing.mobileFriendly'),
    t('landing.freeAccess'),
  ];

  return (
    <div className="min-h-screen relative overflow-hidden font-sans bg-background text-foreground transition-colors duration-300">
      <PremiumBackground />
      <Header />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32">
        <div className="container px-4 mx-auto">
          <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
            <div className="flex-1 text-center lg:text-left z-10">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="inline-flex items-center rounded-full bg-primary/10 backdrop-blur-md border border-primary/20 px-4 py-2 text-sm font-medium text-primary mb-8 shadow-sm"
              >
                <Sparkles className="mr-2 h-4 w-4 text-yellow-500" />
                <span className="bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent font-bold">
                  {t('landing.aiPoweredBadge')}
                </span>
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className="text-5xl lg:text-7xl font-bold tracking-tight mb-6 leading-[1.3] text-foreground"
              >
                {t('landing.learnInYour')} <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 drop-shadow-sm">
                  {t('landing.localLanguage')}
                </span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto lg:mx-0 leading-relaxed"
              >
                {t('landing.heroDescription')}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start"
              >
                <Button asChild size="lg" className="h-14 px-8 text-lg rounded-full shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-1 transition-all duration-300 bg-gradient-to-r from-primary to-purple-600 border-0 text-white">
                  <Link to="/login">
                    {t('common.getStarted')}
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline" className="h-14 px-8 text-lg rounded-full border-2 hover:bg-secondary/50 backdrop-blur-sm transition-all duration-300 bg-background/50 text-foreground">
                  <Link to="/teacherlogin">
                    {t('common.teacherLogin')}
                  </Link>
                </Button>
              </motion.div>
            </div>

            {/* Hero Visual */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, rotate: -5 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="flex-1 relative w-full max-w-xl lg:max-w-none"
            >
              <div className="relative aspect-square md:aspect-[4/3] lg:aspect-square rounded-[3rem] overflow-hidden shadow-2xl border-8 border-white/20 dark:border-white/5 backdrop-blur-sm bg-white/10 dark:bg-black/20 animate-float">
                {/* Abstract 3D Representation */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="relative w-3/4 h-3/4 bg-white/10 backdrop-blur-md rounded-3xl border border-white/30 shadow-inner flex items-center justify-center overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                    <PlayCircle className="w-24 h-24 text-white/80 drop-shadow-lg opacity-80 group-hover:scale-110 transition-transform duration-500" />
                  </div>
                </div>

                {/* Floating Elements */}
                <motion.div
                  animate={{ y: [0, -15, 0] }}
                  transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                  className="absolute top-10 right-10 bg-white/80 dark:bg-slate-800/80 backdrop-blur-md p-4 rounded-2xl shadow-lg"
                >
                  <Languages className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </motion.div>
                <motion.div
                  animate={{ y: [0, 20, 0] }}
                  transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                  className="absolute bottom-10 left-10 bg-white/80 dark:bg-slate-800/80 backdrop-blur-md p-4 rounded-2xl shadow-lg"
                >
                  <GraduationCap className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 relative">
        <div className="container px-4 mx-auto">
          <div className="text-center mb-20">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-4xl lg:text-5xl font-bold mb-6 font-heading text-foreground"
            >
              {t('landing.whyChoose')} <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">{t('header.title')}?</span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-xl text-muted-foreground max-w-2xl mx-auto"
            >
              {t('landing.heroSubtitle')}
            </motion.p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -10 }}
              >
                <Card className="h-full p-8 glass-card border-0 hover:shadow-2xl hover:shadow-primary/10 transition-all duration-300 group">
                  <div className={`mb-6 inline-flex rounded-2xl ${feature.bg} p-4 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className={`h-8 w-8 ${feature.color}`} />
                  </div>
                  <h3 className="mb-3 text-2xl font-bold text-foreground">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-32 bg-secondary/20 backdrop-blur-sm">
        <div className="container px-4 mx-auto">
          <div className="grid gap-16 lg:grid-cols-2 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-4xl lg:text-5xl font-bold mb-8 leading-[1.3] text-foreground">
                {t('landing.educationBoundaries')} <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">
                  {t('landing.noBoundaries')}
                </span>
              </h2>
              <p className="text-lg text-muted-foreground mb-10 leading-relaxed">
                {t('landing.missionStatement')}
              </p>
              <div className="space-y-6">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-4 group"
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                      <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <span className="text-lg font-medium text-foreground group-hover:text-primary transition-colors">{benefit}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9, rotate: 5 }}
              whileInView={{ opacity: 1, scale: 1, rotate: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="aspect-[4/5] rounded-[2.5rem] bg-gradient-to-br from-blue-600 to-purple-600 p-1 shadow-2xl rotate-3 hover:rotate-0 transition-transform duration-500">
                <div className="h-full w-full bg-white dark:bg-slate-900 rounded-[2.4rem] overflow-hidden relative">
                  {/* Decorative Pattern */}
                  <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 to-transparent" />
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center p-10">
                      <div className="w-32 h-32 mx-auto bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center mb-8 animate-pulse-glow">
                        <Globe className="w-16 h-16 text-blue-600" />
                      </div>
                      <h3 className="text-3xl font-bold mb-4 text-foreground">{t('landing.globalStandard')}</h3>
                      <p className="text-muted-foreground">{t('landing.localLanguage')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="container px-4 mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto"
          >
            <Card className="p-12 md:p-20 text-center glass-card border-white/20 dark:border-white/10 overflow-hidden relative">
              {/* Animated Background Blobs */}
              <div className="absolute -top-24 -left-24 w-64 h-64 bg-purple-500/30 rounded-full blur-3xl animate-pulse-glow" />
              <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-blue-500/30 rounded-full blur-3xl animate-pulse-glow delay-1000" />

              <div className="relative z-10">
                <h2 className="text-4xl md:text-5xl font-bold mb-6 font-heading text-foreground">{t('landing.readyToStart')}</h2>
                <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
                  {t('landing.joinStudents')}
                </p>
                <Button asChild size="lg" className="h-16 px-10 text-xl rounded-full shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 bg-primary text-primary-foreground hover:bg-primary/90 border-0">
                  <Link to="/login">
                    {t('landing.createAccount')}
                    <GraduationCap className="ml-3 h-6 w-6" />
                  </Link>
                </Button>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-background/50 backdrop-blur-md py-12">
        <div className="container px-4 mx-auto text-center">
          <p className="text-muted-foreground font-medium">{t('landing.copyright')}</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
